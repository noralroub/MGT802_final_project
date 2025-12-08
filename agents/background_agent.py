"""Background Agent - Extracts study background and research question.

Extracts the clinical context and rationale for the study.
"""

import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class BackgroundAgent:
    """Extracts background information and research question.

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

        prompt = f"""Extract background information and research question from this paper section.

Introduction Section:
{intro_text[:1500]}

Paper Overview:
{paper_overview[:1000]}

Extract:
1. background: A 2-4 sentence summary of the clinical context and why this study was needed.
   Include disease/condition, current knowledge gaps, and clinical significance.
2. research_question: The main question or hypothesis the study addresses (1-2 sentences).

Keep both clear and concise. Focus on what makes this study important.

Respond in JSON:
{{
    "background": "2-4 sentence background...",
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
