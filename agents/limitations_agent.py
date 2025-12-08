"""Limitations Agent - Extracts study limitations.

Extracts design limitations, statistical concerns, and generalizability issues.
"""

import json
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class LimitationsAgent:
    """Extracts study limitations.

    Extracts: limitations (list of limitation statements)
    Uses: Discussion section + Paper overview
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.2):
        """Initialize limitations agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, discussion_text: str, paper_overview: str) -> Dict[str, Any]:
        """Extract study limitations.

        Args:
            discussion_text: Discussion section of the paper
            paper_overview: Paper overview from CombinerAgent

        Returns:
            Dict with limitations list
        """
        if not discussion_text or len(discussion_text.strip()) < 100:
            return self._empty_result()

        prompt = f"""Extract study limitations from this discussion section.

Discussion Section:
{discussion_text[:2000]}

Paper Overview:
{paper_overview[:1000]}

Extract 3-5 key limitations mentioned by the authors. Include:
- Study design limitations (e.g., open-label, single-arm)
- Population limitations (e.g., limited to specific groups)
- Statistical/methodological concerns (e.g., short follow-up, potential bias)
- Generalizability issues

Each limitation should be concise (1-2 sentences) but specific.

Respond in JSON:
{{
    "limitations": [
        "Open-label design without placebo control",
        "Limited to secondary prevention population; results may not apply to primary prevention",
        "Follow-up period of 24 months may not capture long-term durability"
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format={"type": "json_object"},
                max_tokens=500
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Validate
            if 'limitations' not in result:
                result['limitations'] = []
            elif not isinstance(result['limitations'], list):
                result['limitations'] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in limitations agent: {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error in limitations agent: {e}")
            raise

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "limitations": []
        }
