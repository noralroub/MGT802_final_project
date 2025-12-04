"""Vector store module for storing and retrieving embeddings using Chroma."""

import logging
from typing import List, Dict, Tuple
import chromadb
from core.embeddings import embed_texts, embed_query

logger = logging.getLogger(__name__)

# Initialize Chroma client with persistent storage (new API)
CHROMA_DB_PATH = "data/chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


class VectorStore:
    """Vector store for managing embeddings and semantic search."""

    def __init__(self, collection_name: str = "medical_papers"):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the collection to store/retrieve from
        """
        self.collection_name = collection_name
        # Get or create collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        logger.info(f"Initialized VectorStore with collection: {collection_name}")

    def add_chunks(self, chunks: List[str], chunk_ids: List[str] = None) -> None:
        """
        Add text chunks to the vector store.

        Args:
            chunks: List of text chunks
            chunk_ids: Optional list of chunk IDs (auto-generated if not provided)
        """
        try:
            if chunk_ids is None:
                chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]

            # Embed all chunks
            logger.info(f"Embedding {len(chunks)} chunks...")
            embeddings = embed_texts(chunks)

            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=[{"chunk_index": i} for i in range(len(chunks))]
            )
            logger.info(f"Added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for chunks most similar to the query.

        Args:
            query: Query text
            top_k: Number of top results to return

        Returns:
            List of results with documents, distances, and IDs
        """
        try:
            # Embed query
            query_embedding = embed_query(query)

            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # Format results
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'document': doc,
                        'id': results['ids'][0][i] if results['ids'] else None,
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'similarity': 1 - results['distances'][0][i] if results['distances'] else None  # Convert to similarity
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise

    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "num_documents": count,
                "embedding_dimension": 1536
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete collection and recreate
            chroma_client.delete_collection(name=self.collection_name)
            self.collection = chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
