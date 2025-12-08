"""Results Agent - Extracts study results and findings.

Extracts main finding, key results, and adverse events.
"""

import json
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class ResultsAgent:
    """Extracts study results and findings.

    Extracts: main_finding, key_results, adverse_events
    Uses: Results section + Paper overview
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.2):
        """Initialize results agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, results_text: str, paper_overview: str) -> Dict[str, Any]:
        """Extract results and findings.

        Args:
            results_text: Results section of the paper
            paper_overview: Paper overview from CombinerAgent

        Returns:
            Dict with results information
        """
        if not results_text or len(results_text.strip()) < 100:
            return self._empty_result()

        prompt = f"""Extract key results and findings from this results section.

Results Section:
{results_text[:2000]}

Paper Overview:
{paper_overview[:1000]}

Extract:
1. main_finding: The single most important finding from the study.
   Include effect size and confidence interval if available. (1-2 sentences)
2. key_results: List of 3-5 important secondary findings or results.
   Include numbers/statistics where available.
3. adverse_events: List of notable adverse events mentioned, or null if not discussed.

Focus on actual results, not interpretation. Extract numbers as stated in the paper.

Respond in JSON:
{{
    "main_finding": "Semaglutide reduced major adverse cardiovascular events by 26% (HR 0.74, 95% CI 0.58-0.95)",
    "key_results": [
        "Cardiovascular death: 15% reduction",
        "Non-fatal myocardial infarction: reported in 8.2% vs 11.4%",
        "Non-fatal stroke: 3.8% vs 5.1%"
    ],
    "adverse_events": [
        "Gastrointestinal events more common with semaglutide",
        "Serious adverse events: 11.5% vs 13.4%"
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format={"type": "json_object"},
                max_tokens=600
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Validate
            if 'main_finding' not in result:
                result['main_finding'] = None
            if 'key_results' not in result:
                result['key_results'] = []
            elif not isinstance(result['key_results'], list):
                result['key_results'] = []

            if 'adverse_events' not in result:
                result['adverse_events'] = []
            elif not isinstance(result['adverse_events'], list):
                result['adverse_events'] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in results agent: {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error in results agent: {e}")
            raise

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "main_finding": None,
            "key_results": [],
            "adverse_events": []
        }
