"""Summary Agent - Summarizes paper chunks for iterative summaries pipeline.

Summarizes 10% chunks of a clinical trial paper to create digestible summaries.
Multiple summary agents run in parallel, then are combined into a paper overview.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class SummaryAgent:
    """Summarizes a 10% chunk of a clinical trial paper.

    Purpose: Create digestible summaries of paper sections that can be
    combined to form a comprehensive paper overview. This overview helps
    downstream specialized agents extract more accurate information.
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """Initialize summary agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation (lower = more focused)
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, chunk_text: str, chunk_number: int = 1, total_chunks: int = 10) -> Dict[str, Any]:
        """Summarize a paper chunk.

        Args:
            chunk_text: Text content of the chunk (10% of paper)
            chunk_number: Which chunk this is (1-10)
            total_chunks: Total number of chunks

        Returns:
            Dict with 'summary' and 'key_points' fields
        """
        if not chunk_text or len(chunk_text.strip()) < 100:
            return {
                'summary': 'Chunk too small to summarize.',
                'key_points': []
            }

        prompt = f"""You are summarizing Part {chunk_number}/{total_chunks} of a clinical trial research paper.

Paper Text (Part {chunk_number}):
{chunk_text}

Create a concise summary of this part in 200-300 words. Focus on:
- Main topics covered in this section
- Key findings or information presented
- Study design details if present
- Results or conclusions from this part

Then list 3-5 key points from this part.

Respond in JSON format:
{{
    "summary": "200-300 word summary here",
    "key_points": ["point 1", "point 2", "point 3"]
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

            # Validate structure
            if 'summary' not in result:
                result['summary'] = ''
            if 'key_points' not in result:
                result['key_points'] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in summary agent: {e}")
            return {
                'summary': chunk_text[:500],  # Fallback to raw text
                'key_points': []
            }
        except Exception as e:
            logger.error(f"Error in summary agent: {e}")
            raise
