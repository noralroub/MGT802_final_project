"""Unit tests for QA system."""

import pytest
from config import TEST_PDF_PATH, OPENAI_API_KEY


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not configured")
class TestQASystem:
    """Test QA system functionality."""

    @pytest.fixture
    def qa_system(self):
        """Create a QA system instance."""
        from core.qa import QASystem

        qa = QASystem(pdf_path=TEST_PDF_PATH, model="gpt-3.5-turbo")
        yield qa

    def test_qa_system_initialization(self, qa_system):
        """Test QA system initialization."""
        assert qa_system is not None
        assert qa_system.model == "gpt-3.5-turbo"
        assert qa_system.pdf_ingested

    def test_system_info(self, qa_system):
        """Test getting system information."""
        info = qa_system.get_system_info()

        assert "model" in info
        assert "pdf_ingested" in info
        assert "collection" in info
        assert info["pdf_ingested"]

    def test_generate_answer_returns_dict(self, qa_system):
        """Test that generate_answer returns proper dictionary."""
        query = "What was the primary outcome?"
        result = qa_system.generate_answer(query, top_k=3)

        assert isinstance(result, dict)
        assert "answer" in result
        assert "query" in result
        assert "num_sources" in result
        assert "model" in result

    def test_answer_contains_content(self, qa_system):
        """Test that generated answers contain substantial content."""
        query = "What was the primary cardiovascular outcome?"
        result = qa_system.generate_answer(query, top_k=3)

        # Answer should not be empty
        assert len(result["answer"]) > 0
        # Should contain some text
        assert any(word in result["answer"].lower() for word in ["outcome", "primary", "cardiovascular"])

    def test_answer_with_sources(self, qa_system):
        """Test answer generation with source citations."""
        query = "How many patients were enrolled?"
        result = qa_system.generate_answer_with_sources(query, top_k=3)

        assert "sources" in result
        assert "answer" in result
        assert len(result["sources"]) > 0

        # Each source should have required fields
        for source in result["sources"]:
            assert "source_id" in source
            assert "similarity" in source
            assert "preview" in source

    def test_context_formatting(self, qa_system):
        """Test context formatting."""
        query = "trial design"
        chunks = qa_system.pipeline.retrieve(query, top_k=2)

        context = qa_system._format_context(chunks)

        assert isinstance(context, str)
        assert len(context) > 0
        assert "Source" in context

    def test_batch_query(self, qa_system):
        """Test batch query processing."""
        queries = [
            "What was the primary outcome?",
            "How many patients were enrolled?",
            "What dose was used?"
        ]

        results = qa_system.batch_query(queries, top_k=2)

        assert len(results) == len(queries)
        assert all("query" in r for r in results)

    def test_error_handling_without_pdf(self):
        """Test error handling when PDF not ingested."""
        from core.qa import QASystem

        qa = QASystem(model="gpt-3.5-turbo")

        with pytest.raises(ValueError):
            qa.generate_answer("What was the outcome?")

    def test_answer_references_context(self, qa_system):
        """Test that answers reference the provided context."""
        query = "What was the primary cardiovascular outcome?"
        result = qa_system.generate_answer(query, top_k=3)

        # The answer should be grounded in the context
        # It should mention specific terms from cardiovascular trials
        answer_lower = result["answer"].lower()

        # Check for expected medical terminology
        expected_terms = ["outcome", "death", "stroke", "infarction", "cardiovascular"]
        assert any(term in answer_lower for term in expected_terms)


class TestPromptEngineering:
    """Test prompt engineering functions."""

    def test_system_prompt_quality(self):
        """Test that system prompt is well-formed."""
        from core.qa import QASystem

        qa = QASystem.__new__(QASystem)  # Create instance without __init__
        system_prompt = qa._create_system_prompt()

        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "medical" in system_prompt.lower()

    def test_user_prompt_includes_query_and_context(self):
        """Test that user prompt includes both query and context."""
        from core.qa import QASystem

        qa = QASystem.__new__(QASystem)
        test_query = "What was the outcome?"
        test_context = "Test context about the trial."

        user_prompt = qa._create_user_prompt(test_query, test_context)

        assert test_query in user_prompt
        assert test_context in user_prompt
        assert "QUESTION" in user_prompt
        assert "CONTEXT" in user_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
