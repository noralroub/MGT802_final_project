"""Design Agent - Extracts study design information.

Extracts population, intervention, comparator, and primary outcomes information.
"""

import json
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class DesignAgent:
    """Extracts study design information.

    Extracts: population_size, intervention, comparator, primary_outcomes
    Uses: Methods section + Paper overview
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.1):
        """Initialize design agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation (low = strict)
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, methods_text: str, paper_overview: str) -> Dict[str, Any]:
        """Extract study design information.

        Args:
            methods_text: Methods section of the paper
            paper_overview: Paper overview from CombinerAgent

        Returns:
            Dict with design information
        """
        if not methods_text or len(methods_text.strip()) < 100:
            return self._empty_result()

        prompt = f"""Extract study design information from this methods section.

Methods Section:
{methods_text[:2000]}

Paper Overview:
{paper_overview[:1000]}

Extract:
1. population_size: Total number of participants (as integer, or null if not found)
2. intervention: Name/description of the intervention or treatment group (string)
3. comparator: Name/description of the comparison group (string)
4. primary_outcomes: List of primary outcomes measured (list of strings, 1-5 items)

Be specific and use exact terminology from the paper.
If information is not clearly stated, use null.

Respond in JSON:
{{
    "population_size": 3731,
    "intervention": "Semaglutide 1.0 mg weekly",
    "comparator": "Placebo",
    "primary_outcomes": [
        "Major adverse cardiovascular events",
        "Cardiovascular death"
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

            # Validate and clean
            result = self._validate_result(result)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in design agent: {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error in design agent: {e}")
            raise

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "population_size": None,
            "intervention": None,
            "comparator": None,
            "primary_outcomes": []
        }

    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data."""
        if 'population_size' not in result:
            result['population_size'] = None
        elif result['population_size'] is not None:
            try:
                result['population_size'] = int(result['population_size'])
                if result['population_size'] <= 0:
                    result['population_size'] = None
            except (ValueError, TypeError):
                result['population_size'] = None

        if 'intervention' not in result:
            result['intervention'] = None
        if 'comparator' not in result:
            result['comparator'] = None

        if 'primary_outcomes' not in result:
            result['primary_outcomes'] = []
        elif not isinstance(result['primary_outcomes'], list):
            result['primary_outcomes'] = []

        return result
