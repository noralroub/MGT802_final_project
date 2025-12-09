"""Retrieval pipeline for question-answering over medical papers."""

import logging
from typing import List, Dict
from core.pdf_ingest import pipeline_pdf_to_chunks
from core.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for medical papers."""

    def __init__(self, collection_name: str = "medical_papers"):
        """
        Initialize RAG pipeline.

        Args:
            collection_name: Chroma collection name for vector store
        """
        self.vector_store = VectorStore(collection_name=collection_name)
        self.chunks = []
        logger.info("Initialized RAG pipeline")

    def ingest_pdf(self, pdf_path: str) -> Dict:
        """
        Ingest a PDF and add all chunks to the vector store.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Ingesting PDF: {pdf_path}")

            # Clear previous data to avoid mixing papers
            self.vector_store.clear_collection()
            logger.info("Cleared previous vector store data")

            # Parse PDF into chunks
            result = pipeline_pdf_to_chunks(pdf_path)
            self.chunks = result["chunks"]

            # Generate unique chunk IDs with PDF path hash to avoid collisions
            import hashlib
            pdf_hash = hashlib.md5(pdf_path.encode()).hexdigest()[:8]
            chunk_ids = [f"chunk_{pdf_hash}_{i}" for i in range(len(self.chunks))]

            # Add to vector store
            self.vector_store.add_chunks(self.chunks, chunk_ids)

            return {
                "status": "success",
                "pdf_path": pdf_path,
                "num_chunks": len(self.chunks),
                "metadata": result["metadata"]
            }

        except Exception as e:
            logger.error(f"Error ingesting PDF: {e}")
            raise

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Query text
            top_k: Number of top results to return

        Returns:
            List of relevant chunks with scores
        """
        try:
            logger.info(f"Retrieving chunks for query: {query[:50]}...")
            results = self.vector_store.search(query, top_k=top_k)
            return results

        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            raise

    def get_context(self, query: str, top_k: int = 5) -> str:
        """
        Get concatenated context from top-k retrieved chunks.

        Args:
            query: Query text
            top_k: Number of chunks to retrieve

        Returns:
            Concatenated context as string
        """
        try:
            results = self.retrieve(query, top_k=top_k)
            context = "\n\n".join([result["document"] for result in results])
            return context

        except Exception as e:
            logger.error(f"Error getting context: {e}")
            raise

    def get_retrieval_stats(self, query: str, top_k: int = 5) -> Dict:
        """
        Get detailed stats about retrieval for a query.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            Dictionary with retrieval statistics
        """
        try:
            results = self.retrieve(query, top_k=top_k)

            return {
                "query": query,
                "num_results": len(results),
                "results": [
                    {
                        "rank": i + 1,
                        "chunk_id": r["id"],
                        "similarity": r["similarity"],
                        "preview": r["document"][:150] + "..." if len(r["document"]) > 150 else r["document"]
                    }
                    for i, r in enumerate(results)
                ]
            }

        except Exception as e:
            logger.error(f"Error getting retrieval stats: {e}")
            raise

    def get_collection_info(self) -> Dict:
        """Get information about the loaded collection."""
        return self.vector_store.get_collection_info()
