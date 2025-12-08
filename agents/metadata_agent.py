"""Metadata Agent - Extracts paper metadata (title, authors, journal, DOI, study type).

Extracts bibliographic information and study classification from abstract and overview.
"""

import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class MetadataAgent:
    """Extracts paper metadata.

    Extracts: title, authors, journal, year, DOI, study_type
    Uses: Abstract section + Paper overview
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.1):
        """Initialize metadata agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation (very low = strict)
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, abstract_text: str, paper_overview: str) -> Dict[str, Any]:
        """Extract metadata from abstract and overview.

        Args:
            abstract_text: The abstract section from the paper
            paper_overview: The combined overview from CombinerAgent

        Returns:
            Dict with metadata fields
        """
        if not abstract_text or len(abstract_text.strip()) < 50:
            return self._empty_result()

        prompt = f"""Extract metadata from this research paper abstract and overview.

Abstract:
{abstract_text[:1000]}

Paper Overview:
{paper_overview[:1500]}

Extract the following fields:
1. title: The paper title (exact as written)
2. authors: List of author names (from abstract if available)
3. journal: Journal name (if mentioned)
4. year: Publication year (as number)
5. doi: DOI (as string, without URL)
6. study_type: Type of study - one of: RCT, observational, cohort, case-control, meta-analysis, other

IMPORTANT: Only extract information that is clearly present in the text.
If a field is not found, use null.

Respond in JSON:
{{
    "title": "exact title",
    "authors": ["Author One", "Author Two"],
    "journal": "Journal Name",
    "year": 2023,
    "doi": "10.xxxx/xxxxx",
    "study_type": "RCT"
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

            # Validate and clean up
            result = self._validate_result(result)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in metadata agent: {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error in metadata agent: {e}")
            raise

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "title": None,
            "authors": [],
            "journal": None,
            "year": None,
            "doi": None,
            "study_type": None
        }

    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted metadata."""
        # Ensure required fields exist
        if 'title' not in result:
            result['title'] = None
        if 'authors' not in result:
            result['authors'] = []
        elif not isinstance(result['authors'], list):
            result['authors'] = []

        if 'journal' not in result:
            result['journal'] = None
        if 'year' not in result:
            result['year'] = None
        elif result['year'] is not None:
            try:
                result['year'] = int(result['year'])
            except (ValueError, TypeError):
                result['year'] = None

        if 'doi' not in result:
            result['doi'] = None
        if 'study_type' not in result:
            result['study_type'] = None

        # Validate study_type
        valid_types = {'RCT', 'observational', 'cohort', 'case-control', 'meta-analysis', 'other'}
        if result['study_type'] not in valid_types and result['study_type'] is not None:
            result['study_type'] = 'other'

        return result
