"""Embeddings module for converting text to vectors using OpenAI."""

import logging
from typing import List
from openai import OpenAI
from config import OPENAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def embed_text(text: str) -> List[float]:
    """
    Convert text to embedding vector using OpenAI's embedding model.

    Args:
        text: Text to embed

    Returns:
        Embedding vector (list of floats, dimension 1536)
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error embedding text: {e}")
        raise


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert multiple texts to embedding vectors.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    try:
        response = client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL
        )
        # Sort by index to ensure correct order
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [e.embedding for e in embeddings]
    except Exception as e:
        logger.error(f"Error embedding texts: {e}")
        raise


def embed_query(query: str) -> List[float]:
    """
    Convert query string to embedding vector.

    Args:
        query: Query text

    Returns:
        Query embedding vector
    """
    return embed_text(query)
