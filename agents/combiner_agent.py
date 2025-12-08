"""Combiner Agent - Merges 10 summaries into a comprehensive paper overview.

Takes the outputs from 10 SummaryAgents and combines them into a single,
coherent paper overview that provides context for all downstream agents.
"""

import json
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class CombinerAgent:
    """Combines 10 paper chunk summaries into a comprehensive overview.

    Purpose: Merge partial summaries into a unified overview that provides
    context for specialized extraction agents. This overview helps them
    understand the paper's scope, design, and findings.
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """Initialize combiner agent.

        Args:
            model: OpenAI model to use
            temperature: Temperature for generation (lower = more focused)
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def extract(self, summaries: List[Dict[str, Any]]) -> str:
        """Combine chunk summaries into a comprehensive overview.

        Args:
            summaries: List of summary dicts from SummaryAgent
                      Each should have 'summary' and 'key_points'

        Returns:
            Single comprehensive paper overview (string)
        """
        if not summaries:
            return "No summaries provided."

        # Extract and organize summaries
        summary_texts = [
            f"Part {i+1}:\n{s.get('summary', '')}"
            for i, s in enumerate(summaries)
        ]

        # Extract all key points
        all_key_points = []
        for s in summaries:
            points = s.get('key_points', [])
            if isinstance(points, list):
                all_key_points.extend(points)

        combined_summaries = "\n\n".join(summary_texts)
        key_points_text = "\n".join([f"- {p}" for p in all_key_points[:20]])

        prompt = f"""You are combining summaries from all 10 parts of a clinical trial research paper.

Part Summaries:
{combined_summaries}

Key Points from All Parts:
{key_points_text}

Create a comprehensive 1-2 page overview of this paper. Include:

1. **Study Overview**: What is this study about? (2-3 sentences)
2. **Study Design**: Type of study, population, intervention, comparator
3. **Methods**: Key methodological details
4. **Main Findings**: Primary outcomes and results
5. **Implications**: What does this study mean?
6. **Limitations**: Any obvious limitations mentioned

Make it cohesive - not just a list of summaries. This overview will be used by
specialized agents to extract specific data, so be thorough and clear.

Keep it under 1000 words."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1200
            )

            overview = response.choices[0].message.content
            return overview

        except Exception as e:
            logger.error(f"Error in combiner agent: {e}")
            # Fallback: join the summaries
            return combined_summaries
