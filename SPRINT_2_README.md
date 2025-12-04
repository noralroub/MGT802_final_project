# Sprint 2: Embeddings & Vector Store

## Overview

Sprint 2 builds a Retrieval-Augmented Generation (RAG) system on top of Sprint 1's PDF parsing foundation.

**Components**:
- **`core/embeddings.py`** - Convert text to vectors using OpenAI's embedding API
- **`core/vector_store.py`** - Store and search embeddings with Chroma DB
- **`core/retrieval.py`** - End-to-end RAG pipeline for question answering

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...your-key-here...
```

Or set as environment variable:
```bash
export OPENAI_API_KEY=sk-...your-key-here...
```

You can get a free API key from: https://platform.openai.com/api-keys

## Usage

### Basic RAG Pipeline

```python
from core.retrieval import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Ingest a PDF
result = pipeline.ingest_pdf("data/papers/NEJMoa2307563.pdf")
print(f"Ingested {result['num_chunks']} chunks")

# Retrieve relevant chunks for a query
query = "What was the primary cardiovascular outcome?"
chunks = pipeline.retrieve(query, top_k=5)

for i, chunk in enumerate(chunks, 1):
    print(f"\n{i}. Similarity: {chunk['similarity']:.4f}")
    print(f"   {chunk['document'][:200]}...")

# Get concatenated context for LLM
context = pipeline.get_context(query, top_k=3)
print(f"\nContext:\n{context}")
```

### Debug Script

Test the retrieval system with sample queries:

```bash
python3 debug_retrieval.py
```

This will:
1. Ingest the test PDF
2. Run 5 sample queries
3. Show top-3 results for each query
4. Save results to `data/debug_output/retrieval_results.json`

## Architecture

### Embeddings Flow

```
Text Input
    ↓
OpenAI API (text-embedding-3-small)
    ↓
1536-dimensional Vector
    ↓
Stored in Chroma DB
```

### Retrieval Flow

```
Question
    ↓
Embed Question (OpenAI)
    ↓
Query Chroma DB (cosine similarity)
    ↓
Return Top-K Chunks
    ↓
Format Results
```

### Vector Store

- **Type**: Chroma DB (local, persistent)
- **Location**: `data/chroma_db/`
- **Embedding Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Similarity Metric**: Cosine similarity
- **Persistence**: Automatic (data survives restarts)

## Testing

### Unit Tests

```bash
python3 -m pytest tests/test_retrieval.py -v
```

**Note**: Tests require `OPENAI_API_KEY` to be set. Tests will be skipped if the API key is not configured.

### Test Coverage

- Vector store creation and initialization
- PDF ingestion and chunk embedding
- Retrieval accuracy and ranking
- Result formatting and statistics
- Collection management

## Implementation Details

### OpenAI Embeddings

- **Model**: `text-embedding-3-small` (~300K tokens free monthly)
- **Dimension**: 1536 (dense representation)
- **Cost**: ~$0.02 per 1M tokens
- **Speed**: ~1000 embeddings/sec

### Chroma Vector Store

- **Persistence**: DuckDB backend stored in `data/chroma_db/`
- **Index**: HNSW (hierarchical navigable small world)
- **Distance Metric**: Cosine similarity (default)
- **API**: Simple and intuitive

## Performance

### Single PDF (20 chunks)

- **Embedding Time**: ~2-3 seconds (first run, due to API latency)
- **Query Time**: ~1-2 seconds (includes API call for query embedding)
- **Memory**: ~50-100MB (Chroma DB + cache)

### Typical Query Results

Example query: "What was the primary outcome?"

```
1. Similarity: 0.8234
   "primary cardiovascular end point was a composite of death..."

2. Similarity: 0.7891
   "A primary cardiovascular end-point event occurred in 569..."

3. Similarity: 0.7145
   "Results at NEJM.org - A total of 17,604 patients..."
```

## Next Steps

**Sprint 3** will integrate this RAG pipeline with an LLM to:
1. Take retrieved chunks as context
2. Generate natural language answers to questions
3. Format answers for visual abstract generation

## Troubleshooting

### Error: "OpenAI API key not configured"

Make sure `.env` file exists and contains `OPENAI_API_KEY=sk-...`

### Error: "Rate limit exceeded"

OpenAI has rate limits. Wait a few seconds before retrying.

### Vector Store Issues

If Chroma DB gets corrupted, delete `data/chroma_db/` and restart:
```bash
rm -rf data/chroma_db/
```

The vector store will be recreated on next ingestion.

## References

- [OpenAI Embeddings Docs](https://platform.openai.com/docs/guides/embeddings)
- [Chroma DB Docs](https://docs.trychroma.com/)
- [RAG Architecture](https://www.rfc.ai/rag)
