"""Phase 2 Orchestrator - Coordinates the full extraction pipeline.

Orchestrates the 3-stage extraction process:
1. Parallel summaries → Paper overview
2. Specialized extraction (5 agents in parallel)
3. Fact-checking
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from core.pdf_ingest import pipeline_pdf_to_chunks, detect_sections
from agents.summary_agent import SummaryAgent
from agents.combiner_agent import CombinerAgent
from agents.metadata_agent import MetadataAgent
from agents.background_agent import BackgroundAgent
from agents.design_agent import DesignAgent
from agents.results_agent import ResultsAgent
from agents.limitations_agent import LimitationsAgent
from agents.fact_checker import FactChecker

logger = logging.getLogger(__name__)


class Phase2Orchestrator:
    """Orchestrates the full Phase 2 extraction pipeline.

    3-Stage Process:
    1. Generate paper overview (10 parallel summaries + combiner)
    2. Extract specialized information (5 agents in parallel)
    3. Validate with fact-checker
    """

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize orchestrator.

        Args:
            model: OpenAI model to use for all agents
        """
        self.model = model
        self.summary_agent = SummaryAgent(model=model)
        self.combiner_agent = CombinerAgent(model=model)
        self.metadata_agent = MetadataAgent(model=model)
        self.background_agent = BackgroundAgent(model=model)
        self.design_agent = DesignAgent(model=model)
        self.results_agent = ResultsAgent(model=model)
        self.limitations_agent = LimitationsAgent(model=model)
        self.fact_checker = FactChecker()

    def extract_all(self, pdf_path: str) -> Dict[str, Any]:
        """Run full extraction pipeline on a PDF.

        Args:
            pdf_path: Path to clinical trial PDF

        Returns:
            Dict with all extracted information
        """
        logger.info(f"Starting extraction pipeline for {pdf_path}")

        # Cache the ingest result to avoid double PDF processing
        self._cached_ingest = pipeline_pdf_to_chunks(pdf_path)

        # Stage 1: Generate paper overview
        logger.info("Stage 1: Generating paper overview...")
        overview = self._generate_overview()
        logger.info("✓ Paper overview generated")

        # Stage 2: Extract specialized information
        logger.info("Stage 2: Extracting specialized information...")
        extracted = self._extract_specialized(overview)
        logger.info("✓ Specialized extraction complete")

        # Clear cache
        self._cached_ingest = None

        # Stage 3: Fact-check
        logger.info("Stage 3: Validating extracted data...")
        extracted, validation_issues = self.fact_checker.validate(extracted)
        if validation_issues:
            logger.warning(f"Validation issues found: {len(validation_issues)}")
        logger.info("✓ Fact-checking complete")

        extracted['paper_overview'] = overview
        extracted['validation_issues'] = validation_issues

        logger.info("Extraction pipeline complete")
        return extracted

    def _generate_overview(self) -> str:
        """Stage 1: Generate paper overview from chunks.

        Uses cached ingest result from extract_all() to avoid double-processing.

        Returns:
            Comprehensive paper overview (string)
        """
        # Use cached ingest result (computed once in extract_all)
        ingest_result = self._cached_ingest
        chunks = ingest_result.get("chunks", [])

        if not chunks:
            logger.warning("No chunks found in PDF")
            return "Paper overview: Unable to generate overview from empty chunks."

        # Split into 10 chunks (10% each) - select evenly spaced chunks
        chunk_size = max(1, len(chunks) // 10)
        summary_chunks = [chunks[i] for i in range(0, min(len(chunks), 10 * chunk_size), chunk_size)][:10]

        # If we have fewer than 10 chunks, use all of them
        if len(summary_chunks) == 0:
            summary_chunks = chunks[:10]

        # Use chunks as-is for summary agents (each chunk is already text)
        chunk_texts = summary_chunks

        # Run summary agents in parallel
        summaries = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(
                    self.summary_agent.extract,
                    text,
                    i + 1,
                    len(chunk_texts)
                ): i
                for i, text in enumerate(chunk_texts)
            }

            for future in as_completed(futures):
                try:
                    summary = future.result()
                    summaries.append(summary)
                except Exception as e:
                    logger.error(f"Error in summary agent: {e}")
                    summaries.append({'summary': '', 'key_points': []})

        # Combine summaries into overview
        overview = self.combiner_agent.extract(summaries)
        return overview

    def _extract_section_from_map(self, full_text: str, sections: Dict[str, int], section_name: str) -> str:
        """Extract section text using pre-computed section map (avoids repeated detection).

        Args:
            full_text: Full document text
            sections: Pre-computed section positions from detect_sections()
            section_name: Name of section to extract

        Returns:
            Text content of the section, or empty string if not found
        """
        section_lower = section_name.lower()

        if section_lower not in sections:
            # Only warn once per missing section during orchestration
            logger.debug(f"Section '{section_name}' not found in document")
            return ""

        start_pos = sections[section_lower]

        # Find next section position
        end_pos = len(full_text)
        for pos in sections.values():
            if pos > start_pos:
                end_pos = min(end_pos, pos)

        return full_text[start_pos:end_pos].strip()

    def _pick_text(self, primary: str, fallback: str, min_chars: int = 80) -> str:
        """Select primary text when available, otherwise return fallback."""
        primary_clean = primary.strip() if primary else ""
        if len(primary_clean) >= min_chars:
            return primary_clean

        fallback_clean = fallback.strip() if fallback else ""
        return fallback_clean or primary_clean

    def _extract_specialized(
        self, overview: str
    ) -> Dict[str, Any]:
        """Stage 2: Extract specialized information.

        Args:
            overview: Paper overview from Stage 1

        Returns:
            Dict with all extracted information
        """
        # Use cached ingest result (computed once in extract_all)
        ingest_result = self._cached_ingest
        full_text = ingest_result.get("raw_text", "")
        first_page_text = ingest_result.get("first_page_text", "")

        # Detect sections once, reuse for extraction
        sections = detect_sections(full_text)

        # Extract specific sections using helper function
        abstract = self._extract_section_from_map(full_text, sections, 'abstract')
        intro = self._extract_section_from_map(full_text, sections, 'introduction')
        methods = self._extract_section_from_map(full_text, sections, 'methods')
        results = self._extract_section_from_map(full_text, sections, 'results')
        discussion = self._extract_section_from_map(full_text, sections, 'discussion')

        # Choose best-available text for each agent to reduce empty outputs
        abstract_for_agent = self._pick_text(abstract, first_page_text or overview, min_chars=50)
        intro_for_agent = self._pick_text(intro, overview)
        methods_for_agent = self._pick_text(methods, overview)
        results_for_agent = self._pick_text(results, overview)
        discussion_for_agent = self._pick_text(discussion, overview)

        # Run specialized agents in parallel
        extracted = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all agents
            metadata_future = executor.submit(
                self.metadata_agent.extract, abstract_for_agent, overview, first_page_text or overview
            )
            background_future = executor.submit(
                self.background_agent.extract, intro_for_agent, overview
            )
            design_future = executor.submit(
                self.design_agent.extract, methods_for_agent, overview
            )
            results_future = executor.submit(
                self.results_agent.extract, results_for_agent, overview
            )
            limitations_future = executor.submit(
                self.limitations_agent.extract, discussion_for_agent, overview
            )

            # Collect results
            try:
                extracted['metadata'] = metadata_future.result()
            except Exception as e:
                logger.error(f"Error in metadata extraction: {e}")
                extracted['metadata'] = {}

            try:
                extracted['background'] = background_future.result()
            except Exception as e:
                logger.error(f"Error in background extraction: {e}")
                extracted['background'] = {}

            try:
                extracted['design'] = design_future.result()
            except Exception as e:
                logger.error(f"Error in design extraction: {e}")
                extracted['design'] = {}

            try:
                extracted['results'] = results_future.result()
            except Exception as e:
                logger.error(f"Error in results extraction: {e}")
                extracted['results'] = {}

            try:
                extracted['limitations'] = limitations_future.result()
            except Exception as e:
                logger.error(f"Error in limitations extraction: {e}")
                extracted['limitations'] = {}

        return extracted
