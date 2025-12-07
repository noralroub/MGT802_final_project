"""
Evidence extraction agent that runs the full PDF → RAG → structured outputs flow.

Phase 2 Enhancement: Now includes flexible extraction based on study classification.
- Auto-detects study type and structure using StudyClassifier
- Extracts N outcomes (primary + secondary + exploratory)
- Extracts N arms (flexible number)
- Extracts N safety events (flexible)
- Returns flexible structure for any study type
"""

import json
import logging
from typing import Any, Dict, Optional, List
from openai import OpenAI

from config import OPENAI_API_KEY
from core.retrieval import RAGPipeline
from agents.study_classifier import StudyClassifier

logger = logging.getLogger(__name__)


class EvidenceExtractorAgent:
    """
    Run end-to-end extraction:
    - Ingest PDF and index chunks
    - Extract PICOT, stats, and limitations as JSON
    - Generate a structured abstract (Background/Methods/Results/Conclusions)
    - Produce visual-abstract-ready structured data
    """

    def __init__(self, model: str = "gpt-4", top_k: int = 6, collection_name: str = "medical_papers"):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.top_k = top_k
        self.pipeline = RAGPipeline(collection_name=collection_name)
        self.study_classifier = StudyClassifier(model=model, top_k=top_k, collection_name=collection_name)
        self.pdf_ingested = False
        self.study_classification = None  # Will store classification results

    def ingest_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse and index the PDF for downstream retrieval."""
        result = self.pipeline.ingest_pdf(pdf_path)
        self.pdf_ingested = True
        return result

    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """Parse JSON returned from the LLM, handling stray text."""
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
            return json.loads(text)
        except Exception as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            raise

    def _run_extraction(self, query: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Helper to retrieve context and run a chat completion."""
        if not self.pdf_ingested:
            raise ValueError("PDF not ingested. Call ingest_pdf first.")

        context = self.pipeline.get_context(query, top_k=self.top_k)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n\nCONTEXT:\n{context}"},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return self._safe_json_parse(content)

    def classify_study(self) -> Dict[str, Any]:
        """Auto-detect study type and structure using StudyClassifier."""
        if not self.pdf_ingested:
            raise ValueError("PDF not ingested. Call ingest_pdf first.")

        self.study_classification = self.study_classifier.run_classification()
        return self.study_classification

    def extract_picot(self) -> Dict[str, Any]:
        """Extract PICOT + metadata JSON."""
        system_prompt = (
            "You are an evidence extraction assistant for clinical trials. "
            "Return ONLY valid JSON with no commentary."
        )
        user_prompt = """Extract PICOT from the trial. Use this JSON schema:
{
  "population": {"description": "", "inclusion": [], "exclusion": []},
  "intervention": {"description": "", "arms": []},
  "comparator": {"description": ""},
  "outcomes": {"primary": [], "secondary": []},
  "timeline": {"follow_up": "", "duration": ""},
  "sample_size": {"total": null, "arm_allocation": {}}
}"""
        return self._run_extraction(
            query="patient population inclusion exclusion criteria intervention comparator outcomes follow-up duration sample size",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def extract_outcomes_flexible(self) -> List[Dict[str, Any]]:
        """Extract outcomes based on study classification metadata."""
        if not self.pdf_ingested:
            raise ValueError("PDF not ingested. Call ingest_pdf first.")

        if not self.study_classification:
            raise ValueError("Study not classified. Call classify_study first.")

        num_primary = self.study_classification.get("num_primary_outcomes", 1)
        num_secondary = self.study_classification.get("num_secondary_outcomes", 0)
        primary_names = self.study_classification.get("primary_outcome_names", [])
        secondary_names = self.study_classification.get("secondary_outcome_names", [])

        system_prompt = (
            "You are an evidence extraction assistant. "
            "Extract outcome measures from clinical trial results. "
            "Return ONLY valid JSON with no commentary."
        )

        user_prompt = f"""Extract outcome data from the trial results.

Expected outcomes:
- Primary outcomes ({num_primary}): {', '.join(primary_names) if primary_names else 'To be identified'}
- Secondary outcomes ({num_secondary}): {', '.join(secondary_names) if secondary_names else 'None'}

For each outcome, extract:
1. Outcome name/label
2. Effect measure (e.g., hazard ratio, odds ratio, mean difference, event rate, etc.)
3. Numeric estimate
4. Confidence interval (95% unless otherwise specified)
5. P-value (if reported)
6. Units

Return as JSON array:
{{
  "outcomes": [
    {{
      "name": "...",
      "measure_type": "hazard_ratio|odds_ratio|mean_difference|event_rate|continuous|auc|cmax|other",
      "estimate": 0.0,
      "confidence_interval": {{"lower": 0.0, "upper": 0.0}},
      "p_value": 0.05,
      "units": "...",
      "is_primary": true
    }}
  ]
}}"""

        return self._run_extraction(
            query="primary secondary outcomes effect estimates confidence intervals p-values results",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def extract_safety_events_flexible(self) -> List[Dict[str, Any]]:
        """Extract flexible number of safety/adverse events."""
        if not self.pdf_ingested:
            raise ValueError("PDF not ingested. Call ingest_pdf first.")

        system_prompt = (
            "You are a clinical safety analyst. "
            "Extract all safety and adverse event data from the trial. "
            "Return ONLY valid JSON with no commentary."
        )

        user_prompt = """Extract all reported adverse events and safety data.

For each event, extract:
1. Event name
2. Event type (gastrointestinal, cardiovascular, laboratory, serious, discontinuation, etc.)
3. Incidence in each arm (count and/or percentage)
4. Whether it led to discontinuation
5. Whether it was a serious adverse event

Return as JSON:
{
  "safety_events": [
    {
      "event_name": "...",
      "event_type": "gastrointestinal|cardiovascular|laboratory|serious|discontinuation|other",
      "arm_data": {
        "arm_label": {"percent": 0.0, "count": 0}
      },
      "serious": false,
      "led_to_discontinuation": false,
      "notes": "..."
    }
  ]
}"""

        return self._run_extraction(
            query="adverse events safety serious events discontinuations side effects gastrointestinal cardiovascular laboratory",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def extract_arms_flexible(self) -> List[Dict[str, Any]]:
        """Extract flexible number of treatment arms."""
        if not self.pdf_ingested:
            raise ValueError("PDF not ingested. Call ingest_pdf first.")

        if not self.study_classification:
            raise ValueError("Study not classified. Call classify_study first.")

        num_arms = self.study_classification.get("num_arms", 2)
        arm_labels = self.study_classification.get("arm_labels", [])

        system_prompt = (
            "You are an evidence extraction assistant. "
            "Extract treatment arm allocation data. "
            "Return ONLY valid JSON with no commentary."
        )

        user_prompt = f"""Extract treatment arm allocation data.

Expected arms ({num_arms}): {', '.join(arm_labels) if arm_labels else 'To be identified'}

For each arm, extract:
1. Arm label/name
2. Total allocated
3. Total analyzed
4. Total completed
5. Brief description of intervention

Return as JSON:
{{
  "arms": [
    {{
      "label": "...",
      "n_allocated": 0,
      "n_analyzed": 0,
      "n_completed": 0,
      "description": "..."
    }}
  ]
}}"""

        return self._run_extraction(
            query="treatment arms allocation randomization enrollment sample size",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def extract_stats(self) -> Dict[str, Any]:
        """Extract key numeric results."""
        system_prompt = (
            "You are an evidence extraction assistant for clinical trials. "
            "Return ONLY valid JSON with no commentary."
        )
        user_prompt = """Extract key numeric results. Use this JSON schema:
{
  "primary_outcome": {"effect": "", "estimate": "", "ci": "", "p_value": "", "units": ""},
  "secondary_outcomes": [],
  "event_rates": {"arm_1": {"label": "", "value_percent": null}, "arm_2": {"label": "", "value_percent": null}},
  "safety": {"adverse_events": "", "serious_adverse_events": "", "dropouts": ""}
}"""
        return self._run_extraction(
            query="primary and secondary outcomes effect sizes hazard ratio odds ratio confidence intervals p-values event rates safety and adverse events",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def extract_limitations(self) -> Dict[str, Any]:
        """Extract limitations and biases."""
        system_prompt = (
            "You are an evidence extraction assistant for clinical trials. "
            "Return ONLY valid JSON with no commentary."
        )
        user_prompt = """Extract limitations. Use this JSON schema:
{
  "limitations": [],
  "bias_risks": [],
  "generalizability": ""
}"""
        return self._run_extraction(
            query="limitations biases missing data generalizability and threats to validity",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def generate_structured_abstract(self, picot: Dict[str, Any], stats: Dict[str, Any], limitations: Dict[str, Any]) -> Dict[str, str]:
        """Generate structured abstract text."""
        system_prompt = (
            "You are an expert medical writer. Write a concise structured abstract from provided data. "
            "Return ONLY valid JSON."
        )
        user_prompt = f"""Create a structured abstract with sections Background, Methods, Results, Conclusions.
Use this JSON schema:
{{
  "background": "",
  "methods": "",
  "results": "",
  "conclusions": ""
}}

PICOT: {json.dumps(picot)}
STATS: {json.dumps(stats)}
LIMITATIONS: {json.dumps(limitations)}"""

        return self._run_extraction(
            query="trial background methods results conclusions", system_prompt=system_prompt, user_prompt=user_prompt
        )

    def generate_visual_data(
        self,
        picot: Dict[str, Any],
        stats: Dict[str, Any],
        limitations: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Produce visual-abstract-ready structured data aligned with VisualAbstractGenerator expectations.
        """
        system_prompt = (
            "You are producing structured data for a visual abstract of a clinical trial. "
            "Be concise and numeric. Return ONLY JSON."
        )
        user_prompt = f"""Fill this JSON schema. Use numbers where possible; if unknown, set to null or empty string.
{{
  "trial_info": {{"title": "", "drug": "", "indication": "", "trial_name": "", "publication": ""}},
  "population": {{"total_enrolled": null, "arm_1_label": "", "arm_1_size": null, "arm_2_label": "", "arm_2_size": null, "age_mean": null}},
  "primary_outcome": {{"label": "", "effect_measure": "", "estimate": "", "ci": "", "p_value": ""}},
  "event_rates": {{"arm_1_percent": null, "arm_2_percent": null}},
  "adverse_events": {{"summary": "", "notable": []}},
  "dosing": {{"description": ""}},
  "body_weight": {{"arm_1_change_percent": null, "arm_2_change_percent": null}},
  "conclusions": []
}}

PICOT: {json.dumps(picot)}
STATS: {json.dumps(stats)}
LIMITATIONS: {json.dumps(limitations)}"""

        return self._run_extraction(
            query="trial name population size dosing event rates primary outcome conclusions adverse events body weight change",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def run_full_extraction(self, pdf_path: str) -> Dict[str, Any]:
        """
        Convenience method to ingest and run all extraction steps.

        Pipeline:
        1. Ingest PDF and build RAG index
        2. Classify study type and structure
        3. Extract PICOT and general metadata
        4. Extract outcomes (flexible based on classification)
        5. Extract safety events (flexible)
        6. Extract treatment arms (flexible)
        7. Extract limitations
        8. Generate structured abstract
        9. Generate visual abstract data

        Returns flexible extraction results supporting any study type.
        """
        self.ingest_pdf(pdf_path)

        # Step 1: Classify study to guide flexible extraction
        study_classification = self.classify_study()
        logger.info(f"Study classified as: {study_classification.get('study_type')} "
                   f"with {study_classification.get('num_arms')} arms, "
                   f"{study_classification.get('num_primary_outcomes')} primary outcomes")

        # Step 2: Extract core evidence components
        picot = self.extract_picot()
        limitations = self.extract_limitations()

        # Step 3: Extract flexible outcomes (works for any number of primary/secondary)
        outcomes_data = self.extract_outcomes_flexible()

        # Step 4: Extract flexible safety events (works for any number of events)
        safety_data = self.extract_safety_events_flexible()

        # Step 5: Extract flexible treatment arms (works for 2, 3, 5+ arms)
        arms_data = self.extract_arms_flexible()

        # Step 6: Generate narrative summaries
        structured_abstract = self.generate_structured_abstract(picot, outcomes_data, limitations)
        visual_data = self.generate_visual_data(picot, outcomes_data, limitations)

        return {
            "study_classification": study_classification,
            "picot": picot,
            "outcomes": outcomes_data,
            "safety_events": safety_data,
            "arms": arms_data,
            "limitations": limitations,
            "structured_abstract": structured_abstract,
            "visual_data": visual_data,
            "model": self.model,
            "top_k": self.top_k,
        }
