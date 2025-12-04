"""Evidence extraction agent that runs the full PDF → RAG → structured outputs flow."""

import json
import logging
from typing import Any, Dict, Optional
from openai import OpenAI

from config import OPENAI_API_KEY
from core.retrieval import RAGPipeline

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
        self.pdf_ingested = False

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
        """Convenience method to ingest and run all extraction steps."""
        self.ingest_pdf(pdf_path)
        picot = self.extract_picot()
        stats = self.extract_stats()
        limitations = self.extract_limitations()
        structured_abstract = self.generate_structured_abstract(picot, stats, limitations)
        visual_data = self.generate_visual_data(picot, stats, limitations)

        return {
            "picot": picot,
            "stats": stats,
            "limitations": limitations,
            "structured_abstract": structured_abstract,
            "visual_data": visual_data,
            "model": self.model,
            "top_k": self.top_k,
        }
