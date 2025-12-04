"""Unit tests for retrieval system."""

import pytest
import os
from config import TEST_PDF_PATH, OPENAI_API_KEY


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not configured")
class TestRAGPipeline:
    """Test RAG pipeline functionality."""

    @pytest.fixture
    def pipeline(self):
        """Create a RAG pipeline instance."""
        from core.retrieval import RAGPipeline
        pipeline = RAGPipeline(collection_name="test_medical_papers")
        # Clear any existing data
        pipeline.vector_store.clear_collection()
        yield pipeline
        # Cleanup
        pipeline.vector_store.clear_collection()

    def test_ingest_pdf(self, pipeline):
        """Test PDF ingestion."""
        result = pipeline.ingest_pdf(TEST_PDF_PATH)

        assert result["status"] == "success"
        assert result["num_chunks"] > 0
        assert "metadata" in result

    def test_retrieve_returns_results(self, pipeline):
        """Test that retrieval returns results."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        query = "primary outcome"
        results = pipeline.retrieve(query, top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_retrieve_results_have_required_fields(self, pipeline):
        """Test that retrieval results have required fields."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        query = "cardiovascular outcomes"
        results = pipeline.retrieve(query, top_k=3)

        for result in results:
            assert "document" in result
            assert "id" in result
            assert "similarity" in result
            assert isinstance(result["similarity"], float)

    def test_retrieve_similarity_scores_are_valid(self, pipeline):
        """Test that similarity scores are between 0 and 1."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        query = "trial design"
        results = pipeline.retrieve(query, top_k=5)

        for result in results:
            assert 0 <= result["similarity"] <= 1, f"Invalid similarity: {result['similarity']}"

    def test_get_context_returns_string(self, pipeline):
        """Test that get_context returns concatenated string."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        query = "methods and results"
        context = pipeline.get_context(query, top_k=3)

        assert isinstance(context, str)
        assert len(context) > 0

    def test_get_retrieval_stats(self, pipeline):
        """Test retrieval statistics."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        query = "patient population"
        stats = pipeline.get_retrieval_stats(query, top_k=5)

        assert "query" in stats
        assert "num_results" in stats
        assert "results" in stats
        assert len(stats["results"]) > 0

    def test_collection_info(self, pipeline):
        """Test getting collection information."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        info = pipeline.get_collection_info()

        assert "collection_name" in info
        assert "num_documents" in info
        assert "embedding_dimension" in info
        assert info["num_documents"] > 0

    def test_retrieval_relevance(self, pipeline):
        """Test that retrieval returns relevant results."""
        pipeline.ingest_pdf(TEST_PDF_PATH)

        # Query about primary outcome
        query = "What was the primary cardiovascular outcome?"
        results = pipeline.retrieve(query, top_k=1)

        # Top result should have high similarity
        assert results[0]["similarity"] > 0.5, "Top result has low similarity"

        # Document should contain relevant keywords
        doc_lower = results[0]["document"].lower()
        assert any(keyword in doc_lower for keyword in ["outcome", "primary", "event"])


class TestVectorStore:
    """Test vector store functionality."""

    def test_vector_store_creation(self):
        """Test vector store creation."""
        try:
            from core.vector_store import VectorStore
            store = VectorStore(collection_name="test_store")
        except ValueError:
            # Skip if API key is not configured
            pytest.skip("OpenAI API key not configured")
        assert store is not None
        assert store.collection_name == "test_store"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
