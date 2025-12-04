"""Unit tests for PDF ingestion module."""

import pytest
from core.pdf_ingest import (
    extract_text_from_pdf,
    detect_sections,
    estimate_tokens,
    chunk_text,
    pipeline_pdf_to_chunks,
)
from config import TEST_PDF_PATH


class TestPDFExtraction:
    """Test PDF text extraction."""

    def test_extract_text_returns_non_empty_string(self):
        """Test that extract_text_from_pdf returns non-empty string."""
        text = extract_text_from_pdf(TEST_PDF_PATH)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_extract_text_contains_expected_content(self):
        """Test that extracted text contains expected content."""
        text = extract_text_from_pdf(TEST_PDF_PATH)
        # Check for key terms from Semaglutide paper
        assert "semaglutide" in text.lower()


class TestSectionDetection:
    """Test section detection."""

    def test_detect_sections_finds_methods_and_results(self):
        """Test that detect_sections finds Methods and Results sections."""
        text = extract_text_from_pdf(TEST_PDF_PATH)
        sections = detect_sections(text)

        # Should find at least Methods, Results, Abstract
        assert "methods" in sections or "Methods" in sections.lower()
        assert "results" in sections or "Results" in sections.lower()

    def test_detect_sections_returns_dict_with_positions(self):
        """Test that detect_sections returns dict with integer positions."""
        text = extract_text_from_pdf(TEST_PDF_PATH)
        sections = detect_sections(text)

        assert isinstance(sections, dict)
        for section_name, position in sections.items():
            assert isinstance(section_name, str)
            assert isinstance(position, int)
            assert position >= 0


class TestTokenEstimation:
    """Test token estimation."""

    def test_estimate_tokens_returns_positive_number(self):
        """Test that estimate_tokens returns positive number."""
        text = "This is a test sentence."
        tokens = estimate_tokens(text)
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_estimate_tokens_scales_with_text_length(self):
        """Test that token count scales with text length."""
        short_text = "Hello world"
        long_text = "Hello world " * 100

        short_tokens = estimate_tokens(short_text)
        long_tokens = estimate_tokens(long_text)

        assert long_tokens > short_tokens


class TestChunking:
    """Test text chunking."""

    def test_chunk_text_returns_list_of_chunks(self):
        """Test that chunk_text returns list of strings."""
        text = extract_text_from_pdf(TEST_PDF_PATH)
        chunks = chunk_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunks_are_within_token_size(self):
        """Test that chunks are reasonable size."""
        text = extract_text_from_pdf(TEST_PDF_PATH)
        chunks = chunk_text(text, chunk_size=1024, overlap=128)

        # Verify chunks have reasonable size (not too small, not too large)
        avg_tokens = sum(estimate_tokens(chunk) for chunk in chunks) / len(chunks)

        # Average should be close to target size
        assert 600 < avg_tokens < 1100, f"Average chunk size {avg_tokens} tokens is out of range"

    def test_chunks_preserve_text_coverage(self):
        """Test that chunks contain most of original text."""
        text = extract_text_from_pdf(TEST_PDF_PATH)[:5000]  # Use subset for speed
        chunks = chunk_text(text)

        concatenated = " ".join(chunks)
        # Should have significant coverage (allowing for formatting changes)
        assert len(concatenated) > len(text) * 0.8


class TestPipeline:
    """Test end-to-end pipeline."""

    def test_pipeline_returns_valid_dict(self):
        """Test that pipeline returns dict with required keys."""
        result = pipeline_pdf_to_chunks(TEST_PDF_PATH)

        assert isinstance(result, dict)
        assert "raw_text" in result
        assert "sections" in result
        assert "chunks" in result
        assert "metadata" in result

    def test_pipeline_metadata_is_valid(self):
        """Test that pipeline metadata contains required fields."""
        result = pipeline_pdf_to_chunks(TEST_PDF_PATH)
        metadata = result["metadata"]

        assert "num_pages" in metadata
        assert "total_chars" in metadata
        assert "total_tokens" in metadata
        assert "num_chunks" in metadata
        assert "avg_tokens_per_chunk" in metadata

        # All should be numeric and non-negative
        assert metadata["total_chars"] > 0
        assert metadata["total_tokens"] > 0
        assert metadata["num_chunks"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
