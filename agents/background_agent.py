"""Background Agent - Extracts study background and research question.

Extracts the clinical context and rationale for the study.
"""

import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class BackgroundAgent:
    """Extracts a NEJM/JACC-style trial positioning sentence plus research question.

    Extracts: background, research_question
    Uses: Introduction section + Paper overview
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.2):
        """Initialize background agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, intro_text: str, paper_overview: str) -> Dict[str, Any]:
        """Extract background and research question.

        Args:
            intro_text: Introduction section of the paper
            paper_overview: Paper overview from CombinerAgent

        Returns:
            Dict with background and research_question
        """
        if not intro_text or len(intro_text.strip()) < 50:
            return self._empty_result()

        prompt = f"""You are a medical journal editor. From the content below, generate:

1. background: ONE single sentence that starts with "The first..." and mirrors NEJM/JACC
   positioning blurbs. It must:
   - specify study design elements (randomized, double-blind, head-to-head, etc.)
   - mention intervention and comparator, including drug class or delivery if relevant
   - name the target disease/population and risk profile
   - articulate the unmet clinical problem or rationale
   - stay factual, 25-40 words, no statistics, no outcomes, no extra commentary
2. research_question: 1-2 sentences that clearly capture the clinical hypothesis being tested.

INTRODUCTION:
{intro_text[:1500]}

PAPER OVERVIEW:
{paper_overview[:1000]}

Respond in JSON only:
{{
    "background": "The first...",
    "research_question": "The main research question..."
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format={"type": "json_object"},
                max_tokens=400
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Validate
            if 'background' not in result:
                result['background'] = None
            if 'research_question' not in result:
                result['research_question'] = None

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in background agent: {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error in background agent: {e}")
            raise

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "background": None,
            "research_question": None
        }
