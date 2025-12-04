# Sprint 3: LLM Integration for Answer Generation

## Overview

Sprint 3 completes the RAG (Retrieval-Augmented Generation) pipeline by integrating with OpenAI's GPT to generate natural language answers from retrieved medical trial data.

**Architecture**:
```
Question
    ↓
[RAG Retrieval] Get top-3 relevant chunks
    ↓
[Prompt Engineering] Format context + question
    ↓
[LLM] GPT-3.5-turbo generates answer
    ↓
[Response] Natural language answer with citations
```

## Setup

### 1. Configure OpenAI API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 2. Install Dependencies

All dependencies are already in `requirements.txt`. They were installed in Sprint 2.

### 3. Verify Configuration

```python
from core.qa import QASystem
qa = QASystem(model="gpt-3.5-turbo")
print(qa.get_system_info())
```

## Usage

### Basic QA (Single Question)

```python
from core.qa import QASystem
from config import TEST_PDF_PATH

# Initialize and ingest PDF
qa = QASystem(pdf_path=TEST_PDF_PATH, model="gpt-3.5-turbo")

# Ask a question
result = qa.generate_answer("What was the primary cardiovascular outcome?")

print("Question:", result["query"])
print("Answer:", result["answer"])
print("Sources used:", result["num_sources"])
```

### QA with Source Citations

```python
result = qa.generate_answer_with_sources(
    "How many patients were enrolled?",
    top_k=3
)

print("Answer:", result["answer"])
for source in result["sources"]:
    print(f"[Source {source['source_id']}] {source['preview']}")
```

### Batch Query Processing

```python
questions = [
    "What was the primary outcome?",
    "What dose was used?",
    "What were the adverse events?"
]

results = qa.batch_query(questions, top_k=3)

for result in results:
    print(f"Q: {result['query']}")
    print(f"A: {result['answer']}\n")
```

## Components

### QASystem Class

**Initialization**:
```python
qa = QASystem(
    pdf_path="data/papers/trial.pdf",      # Optional, can be set later
    collection_name="medical_papers",       # Chroma collection name
    model="gpt-3.5-turbo"                  # OpenAI model
)
```

**Methods**:

1. **`ingest_pdf(pdf_path)`** - Load and embed PDF
   - Returns ingestion metadata
   - Raises error if PDF parsing fails

2. **`generate_answer(query, top_k=3, temperature=0.7)`** - Generate single answer
   - Retrieves top-K relevant chunks
   - Calls GPT-3.5-turbo with context
   - Returns answer + metadata

3. **`generate_answer_with_sources(query, top_k=3)`** - Answer with citations
   - Includes detailed source information
   - Shows relevance scores
   - Provides chunk previews

4. **`batch_query(queries, top_k=3)`** - Answer multiple questions
   - Processes list of queries
   - Returns list of results
   - Includes error handling

5. **`get_system_info()`** - System statistics
   - Model name
   - PDF ingestion status
   - Collection metadata

### Prompt Engineering

The system uses two-part prompting for quality answers:

**1. System Prompt** (defines role and behavior):
- Medical research expert specialization
- Context-based reasoning
- Precision and citation guidelines
- Statistical formatting rules

**2. User Prompt** (specific question + context):
- Question clearly stated
- Retrieved context provided
- Citation format instructions

This two-part approach ensures:
- Consistent expert perspective
- Grounded reasoning (no hallucinations)
- Medical terminology accuracy
- Specific, measurable outputs

## Debug Script

Test the QA system with 7 sample questions:

```bash
python3 debug_qa.py
```

Output:
- Displays each question and answer
- Shows sources with relevance scores
- Saves results to `data/debug_output/qa_results.json`
- Prints token usage statistics

## Testing

### Unit Tests

```bash
python3 -m pytest tests/test_qa.py -v
```

**Test Coverage**:
- System initialization and configuration
- PDF ingestion
- Single question answering
- Source citation generation
- Batch query processing
- Error handling
- Prompt formatting
- Answer quality checks

### Manual Testing

Ask custom questions:

```python
qa = QASystem(pdf_path=TEST_PDF_PATH)

custom_questions = [
    "What is the drug being tested?",
    "What disease was the trial for?",
    "What were the main results?"
]

for q in custom_questions:
    result = qa.generate_answer_with_sources(q)
    print(f"\nQ: {q}\nA: {result['answer']}\n")
```

## Configuration Options

### Model Selection

```python
# Fast, cheaper (~$0.002 per 1K tokens)
qa = QASystem(model="gpt-3.5-turbo")

# Slower, better quality (~$0.03 per 1K tokens)
qa = QASystem(model="gpt-4")
```

### Retrieval Settings

```python
# More sources = longer context, higher cost
result = qa.generate_answer(query, top_k=5)  # Default is 3

# Fewer sources = faster, cheaper
result = qa.generate_answer(query, top_k=1)
```

### Temperature Control

```python
# Deterministic (same answer every time)
result = qa.generate_answer(query, temperature=0.0)

# Creative/exploratory
result = qa.generate_answer(query, temperature=1.0)

# Balanced (default)
result = qa.generate_answer(query, temperature=0.7)
```

## Output Format

### Single Answer Result

```json
{
  "answer": "The primary cardiovascular outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke...",
  "query": "What was the primary cardiovascular outcome?",
  "num_sources": 3,
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "tokens_used": 287
}
```

### Answer with Sources

```json
{
  "answer": "...",
  "sources": [
    {
      "source_id": 1,
      "similarity": 0.8234,
      "preview": "primary cardiovascular end point was a composite of death..."
    },
    ...
  ],
  "num_sources": 3
}
```

## Prompt Templates

### System Prompt

The system tells the LLM to:
- Act as medical research expert
- Answer only from provided context
- Include specific numbers/statistics
- Distinguish between trial arms
- Cite sources
- Keep answers concise

### User Prompt

The user prompt:
- Asks the specific question
- Provides retrieved context chunks
- Instructions for response format

Example:
```
Based on the following context from a cardiovascular trial paper, answer this question:

QUESTION: What was the primary outcome?

CONTEXT:
[Source 1, relevance: 82%]
primary cardiovascular end point was a composite of...

[Source 2, relevance: 79%]
Results: A primary cardiovascular end-point event occurred...
```

## Performance & Costs

### Response Time

- **Retrieval**: ~1-2 seconds (includes embedding query)
- **LLM Call**: ~2-5 seconds (API latency)
- **Total per question**: ~3-7 seconds

### API Costs (Approximate)

Using GPT-3.5-turbo on Semaglutide paper (20 chunks):

| Operation | Tokens | Cost |
|-----------|--------|------|
| Embed 20 chunks | ~15,000 | $0.001 |
| Query question | ~100 | <$0.001 |
| LLM answer (7 questions) | ~2,000 | $0.002 |
| **Total for sprint** | ~17,000 | ~$0.003 |

**GPT-3.5-turbo**: ~$0.002 per 1K input + output tokens
**GPT-4**: ~$0.03 per 1K input tokens

## Troubleshooting

### Error: "OpenAI API key not configured"

Make sure `.env` file exists and contains valid key:
```bash
cat .env
# Should show: OPENAI_API_KEY=sk-proj-...
```

### Error: "Rate limit exceeded"

OpenAI has rate limits. Wait 60 seconds and retry.

### Poor Answer Quality

Try these approaches:
1. **Increase `top_k`**: More context = better answers
   ```python
   qa.generate_answer(query, top_k=5)
   ```

2. **Use GPT-4**: Better reasoning
   ```python
   qa = QASystem(model="gpt-4")
   ```

3. **Adjust temperature**: Lower = more deterministic
   ```python
   qa.generate_answer(query, temperature=0.3)
   ```

### Answer is Hallucinating (Not in Context)

The system is designed to minimize hallucinations:
- System prompt emphasizes context-only answers
- Retrieved context is provided as ground truth
- LLM is instructed to say "not in context" if needed

If hallucinations occur:
1. Check retrieved chunks are relevant
2. Review system prompt template
3. Switch to GPT-4 (more reliable)

## Next Steps (Sprint 4)

Sprint 4 will use these answers to generate visual abstracts:
- Extract key numbers/statistics from answers
- Design visual layout
- Create infographics
- Integrate into Streamlit UI

## References

- [OpenAI Chat Completions](https://platform.openai.com/docs/guides/gpt)
- [Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [RAG Architecture](https://www.rfc.ai/rag)
