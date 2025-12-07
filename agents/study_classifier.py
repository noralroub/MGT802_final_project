"""
Study Classifier Agent

Auto-detects study type, design, and structure from PDF context.

This agent answers: "What type of study is this, and what should I be extracting?"

Before flexible extraction, we need to know:
- What type of study (RCT, observational, crossover, etc.)
- How many treatment arms
- How many primary outcomes
- How many secondary outcomes
- Design features (parallel, factorial, etc.)
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

from config import OPENAI_API_KEY
from core.retrieval import RAGPipeline
from schemas.trial_schemas import TrialDesignType

logger = logging.getLogger(__name__)


class StudyClassifier:
    """
    Classifies study type and structure from PDF.

    This agent provides metadata that guides flexible extraction:
    - Study type and design
    - Number of arms
    - Number of outcomes (primary and secondary)
    - Study duration and follow-up
    - Any special design features

    Output informs extraction agent on what to look for.
    """

    def __init__(self, model: str = "gpt-4", top_k: int = 8, collection_name: str = "medical_papers"):
        """
        Initialize study classifier.

        Args:
            model: LLM model (gpt-4 recommended for accuracy)
            top_k: Number of RAG context chunks to retrieve
            collection_name: Vector store collection name
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.top_k = top_k
        self.pipeline = RAGPipeline(collection_name=collection_name)

    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling stray text.

        Args:
            text: Response text from LLM

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If JSON cannot be parsed
        """
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
            return json.loads(text)
        except Exception as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            logger.error(f"Response text: {text[:500]}")
            raise ValueError(f"Cannot parse classifier response: {e}") from e

    def classify_study(self, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify study type and structure.

        Extracts key metadata about the study to guide downstream extraction.

        Args:
            context: Optional RAG context (retrieved internally if not provided)

        Returns:
            Dictionary with study classification metadata:
            {
                "study_type": "randomized_controlled_trial",
                "design": "parallel",
                "num_arms": 2,
                "arm_labels": ["Drug A", "Placebo"],
                "num_primary_outcomes": 1,
                "primary_outcome_names": ["Serious cardiovascular events"],
                "num_secondary_outcomes": 0,
                "secondary_outcome_names": [],
                "has_safety_analysis": true,
                "has_pharmacokinetic_data": false,
                "follow_up_duration": "40 months",
                "special_design_features": "",
                "confidence": "high",
                "notes": ""
            }
        """

        if context is None:
            context = self.pipeline.get_context(
                "study design type structure arms outcomes follow-up duration methodology",
                top_k=self.top_k,
            )

        system_prompt = """You are an expert clinical study analyst with deep knowledge of study designs.
Your task is to classify the study type and structure from the provided text.
Return ONLY valid JSON with no commentary, explanations, or extra text."""

        user_prompt = """Analyze this study and classify it. Answer these questions:

1. What is the STUDY TYPE? (e.g., "randomized_controlled_trial", "observational", "cohort", "case_control", "cross_sectional")
2. What is the DESIGN? (e.g., "parallel", "crossover", "factorial", or "not_applicable")
3. How many TREATMENT ARMS? List the arm labels.
4. How many PRIMARY OUTCOMES? What are they?
5. How many SECONDARY OUTCOMES? List them.
6. Is there SAFETY/ADVERSE EVENT analysis?
7. Is there PHARMACOKINETIC data (AUC, Cmax, etc.)?
8. What is the FOLLOW-UP DURATION?
9. Any special design features? (e.g., "multicenter", "double-blind", "adaptive")
10. How confident are you in this classification? (high/medium/low)

Return this JSON (and ONLY this JSON):
{
  "study_type": "randomized_controlled_trial|observational|cohort|case_control|cross_sectional|other",
  "design": "parallel|crossover|factorial|not_applicable|other",
  "num_arms": 0,
  "arm_labels": ["...", "..."],
  "num_primary_outcomes": 0,
  "primary_outcome_names": ["..."],
  "num_secondary_outcomes": 0,
  "secondary_outcome_names": ["..."],
  "has_safety_analysis": false,
  "has_pharmacokinetic_data": false,
  "follow_up_duration": "...",
  "special_design_features": "...",
  "confidence": "high|medium|low",
  "notes": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n\nSTUDY TEXT:\n{context}"},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistency
            )
            content = response.choices[0].message.content
            return self._safe_json_parse(content)
        except Exception as e:
            logger.error(f"Error calling classifier: {e}")
            raise

    def get_design_enum(self, design_str: str) -> TrialDesignType:
        """
        Convert design string to TrialDesignType enum.

        Args:
            design_str: Design string from classifier

        Returns:
            Corresponding TrialDesignType enum value

        Raises:
            ValueError: If design string doesn't match known types
        """
        design_map = {
            "parallel": TrialDesignType.PARALLEL,
            "crossover": TrialDesignType.CROSSOVER,
            "factorial": TrialDesignType.FACTORIAL,
            "randomized_controlled_trial": TrialDesignType.RCT,
            "observational": TrialDesignType.OBSERVATIONAL,
            "cohort": TrialDesignType.COHORT,
            "case_control": TrialDesignType.CASE_CONTROL,
            "cross_sectional": TrialDesignType.CROSS_SECTIONAL,
            "pharmacokinetic": TrialDesignType.PHARMACOKINETIC,
        }

        design_lower = design_str.lower().strip()
        if design_lower in design_map:
            return design_map[design_lower]

        logger.warning(f"Unknown design type: {design_str}, defaulting to UNKNOWN")
        return TrialDesignType.UNKNOWN

    def validate_classification(self, classification: Dict[str, Any]) -> bool:
        """
        Validate classification metadata.

        Checks:
        - num_arms >= 1
        - num_primary_outcomes >= 1
        - arm_labels has correct count
        - outcome names match counts

        Args:
            classification: Classifier output

        Returns:
            True if valid, False otherwise
        """
        # Check arms
        if classification.get("num_arms", 0) < 1:
            logger.warning("Classification has < 1 arm")
            return False

        arm_labels = classification.get("arm_labels", [])
        if len(arm_labels) != classification.get("num_arms", 0):
            logger.warning(
                f"Arm count ({classification.get('num_arms')}) doesn't match "
                f"arm_labels length ({len(arm_labels)})"
            )
            return False

        # Check primary outcomes
        if classification.get("num_primary_outcomes", 0) < 1:
            logger.warning("Classification has < 1 primary outcome")
            return False

        primary_names = classification.get("primary_outcome_names", [])
        if len(primary_names) != classification.get("num_primary_outcomes", 0):
            logger.warning(
                f"Primary outcome count ({classification.get('num_primary_outcomes')}) "
                f"doesn't match outcome names length ({len(primary_names)})"
            )
            return False

        # Secondary outcomes are optional
        secondary_count = classification.get("num_secondary_outcomes", 0)
        secondary_names = classification.get("secondary_outcome_names", [])
        if secondary_count > 0 and len(secondary_names) != secondary_count:
            logger.warning(
                f"Secondary outcome count ({secondary_count}) "
                f"doesn't match names length ({len(secondary_names)})"
            )
            return False

        return True

    def run_classification(self, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Run full classification with validation.

        Args:
            context: Optional RAG context

        Returns:
            Validated classification result

        Raises:
            ValueError: If classification fails validation
        """
        classification = self.classify_study(context)

        if not self.validate_classification(classification):
            logger.warning("Classification validation failed, but returning anyway")
            # Log but don't fail - extraction will handle gracefully

        return classification

    def summarize_classification(self, classification: Dict[str, Any]) -> str:
        """
        Create human-readable summary of classification.

        Args:
            classification: Classifier output

        Returns:
            Formatted summary string
        """
        summary = (
            f"Study Type: {classification.get('study_type', 'unknown')}\n"
            f"Design: {classification.get('design', 'unknown')}\n"
            f"Arms: {classification.get('num_arms', 0)} "
            f"({', '.join(classification.get('arm_labels', []))})\n"
            f"Primary Outcomes: {classification.get('num_primary_outcomes', 0)} "
            f"({', '.join(classification.get('primary_outcome_names', []))})\n"
            f"Secondary Outcomes: {classification.get('num_secondary_outcomes', 0)}\n"
            f"Follow-up: {classification.get('follow_up_duration', 'not specified')}\n"
            f"Safety Analysis: {classification.get('has_safety_analysis', False)}\n"
            f"Pharmacokinetic Data: {classification.get('has_pharmacokinetic_data', False)}\n"
            f"Confidence: {classification.get('confidence', 'unknown')}"
        )
        return summary
