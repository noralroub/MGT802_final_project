# Sprint 1 Plan: PDF Ingestion & Chunking Foundation

**Duration**: Days 0–1
**Goal**: Validate that PDF parsing and chunking work reliably on a real cardiovascular trial paper before proceeding to RAG/LLM layers.

---

## Overview

Sprint 1 is about **de-risking the foundation**. The entire pipeline depends on clean, complete text extraction and intelligent chunking. If this layer is broken, downstream LLM calls will fail or hallucinate. This sprint focuses on:

- Parsing a real cardiovascular trial PDF reliably
- Detecting paper sections (Methods, Results, etc.)
- Chunking text intelligently while preserving context
- Manual validation of output quality

## Deliverables

1. **Codebase structure** (`core/pdf_ingest.py`, `config.py`, basic repo layout)
2. **PDF parser** supporting pdfplumber or PyPDF
3. **Section detection** (regex-based, cardiovascular trial specific)
4. **Chunking logic** (fixed size ~800–1200 tokens, with overlap)
5. **Test harness** that runs on a single reference PDF and outputs debug artifacts
6. **One working example**: Full pipeline output on test PDF (chunks, sections, quality report)

---

## Tasks

### Task 1.1: Set Up Repository Structure
**Owner**: You
**Status**: Pending
**Effort**: 0.5 hours

Create the directory structure and initial files:
```
project/
├── app.py                      # (stub for now)
├── config.py                   # API keys, constants, model names
├── requirements.txt            # dependencies
├── core/
│   ├── __init__.py
│   ├── pdf_ingest.py          # PDF parsing + chunking
│   ├── embeddings.py          # (stub for Sprint 2)
│   └── vector_store.py        # (stub for Sprint 2)
├── agents/
│   ├── __init__.py
│   ├── evidence_extractor.py  # (stub for Sprint 3)
│   └── abstract_designer.py   # (stub for Sprint 4)
├── pipeline/
│   ├── __init__.py
│   └── visual_abstract_pipeline.py  # (stub for now)
├── evaluation/
│   ├── __init__.py
│   └── eval_utils.py          # (stub for Sprint 6)
├── tests/
│   ├── __init__.py
│   └── test_pdf_ingest.py     # Unit tests for PDF parsing
├── data/
│   ├── test_paper.pdf         # (will be added once sourced)
│   └── debug_output/          # For saving intermediate outputs
└── README.md
```

**Acceptance Criteria**:
- [ ] All directories created
- [ ] `config.py` has placeholder values (API key, model name, chunk size constants)
- [ ] `requirements.txt` includes: `pdfplumber`, `pypdf`, `tiktoken`, `python-dotenv`
- [ ] Repo is clean (no stray files)

---

### Task 1.2: Source a Reference Cardiovascular Trial PDF
**Owner**: You
**Status**: Pending
**Effort**: 0.5 hours

Find one **real** cardiovascular clinical trial PDF that will serve as your test case throughout all 6 sprints.

**Criteria**:
- Published cardiovascular trial (e.g., heart failure, hypertension, ACS)
- ~10–20 pages (not too long, not a poster)
- Has clear sections: Background, Methods, Results, Conclusions
- Publicly available (arXiv, PubMed Central, or open-access journal)

**Where to find**:
- PubMed Central: https://www.ncbi.nlm.nih.gov/pmc/ (search "cardiovascular trial", filter "free full text")
- medRxiv: https://www.medrxiv.org/ (preprints)
- Specific journals: Circulation, JACC, Heart, European Heart Journal (many have open access)

**Acceptance Criteria**:
- [ ] PDF downloaded and saved to `data/test_paper.pdf`
- [ ] You've manually read the first 2 pages and confirmed it has standard structure
- [ ] You know the correct answers for: primary outcome, population size, intervention type, key p-values (for later validation)

---

### Task 1.3: Implement Basic PDF Parser
**Owner**: You
**Status**: Pending
**Effort**: 2 hours

Write `core/pdf_ingest.py` with the following functions:

**Function: `extract_text_from_pdf(pdf_path: str) -> str`**
- Use pdfplumber to extract text from all pages
- Return raw concatenated text
- Handle edge cases: empty pages, PDFs that fail to parse
- Log any warnings (e.g., "Page 5 returned empty text")

**Function: `detect_sections(text: str) -> dict[str, int]`**
- Use regex to find section headers (case-insensitive): "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusions", "References"
- Return dict mapping section name → character position in text
- Example output: `{"Methods": 2543, "Results": 5124, "Discussion": 8901}`
- If a section is not found, log a warning

**Function: `extract_section(text: str, section_name: str) -> str`**
- Given a section name, return the text from that section to the next section
- Handle edge case: if section doesn't exist, return empty string

**Acceptance Criteria**:
- [ ] `extract_text_from_pdf()` returns raw text without errors
- [ ] `detect_sections()` correctly identifies at least "Methods", "Results", "Discussion"
- [ ] `extract_section()` returns clean subsections
- [ ] All functions have docstrings
- [ ] No external API calls (local only)

---

### Task 1.4: Implement Text Chunking
**Owner**: You
**Status**: Pending
**Effort**: 2 hours

Write `core/pdf_ingest.py` (add to existing file):

**Function: `chunk_text(text: str, chunk_size: int = 1024, overlap: int = 128) -> list[str]`**
- Split text into chunks of ~1024 tokens (estimate: ~4 chars per token)
- Add 128-token overlap between chunks
- Use sentence boundaries where possible (don't split mid-sentence)
- Return list of chunks

**Helper: `estimate_tokens(text: str) -> int`**
- Use tiktoken to count actual tokens (install: `pip install tiktoken`)
- Used by chunking logic to ensure accurate chunk sizes

**Function: `pipeline_pdf_to_chunks(pdf_path: str) -> dict`**
- End-to-end: extract → detect sections → chunk all text
- Return dict with:
  ```python
  {
    "raw_text": str,
    "sections": dict[str, str],  # "Methods" → text, etc.
    "chunks": list[str],
    "metadata": {
      "num_pages": int,
      "total_chars": int,
      "total_tokens": int,
      "num_chunks": int,
      "avg_tokens_per_chunk": float
    }
  }
  ```

**Acceptance Criteria**:
- [ ] Chunks are ~1000–1200 tokens (within ±5%)
- [ ] Overlap is ~128 tokens
- [ ] Chunks don't cut off mid-sentence (or minimize)
- [ ] Function returns valid metadata
- [ ] All functions have docstrings

---

### Task 1.5: Build Test Harness & Debug Output
**Owner**: You
**Status**: Pending
**Effort**: 1.5 hours

Write `tests/test_pdf_ingest.py` and a simple CLI script:

**Script: `debug_pdf_ingest.py` (in root)**
```python
# Usage: python debug_pdf_ingest.py data/test_paper.pdf

from core.pdf_ingest import pipeline_pdf_to_chunks

pdf_path = "data/test_paper.pdf"
result = pipeline_pdf_to_chunks(pdf_path)

# Output 1: Print sections found
print("=== SECTIONS DETECTED ===")
for section, text in result["sections"].items():
    print(f"{section}: {len(text)} chars, ~{len(text)//4} tokens")

# Output 2: Print first 5 chunks
print("\n=== FIRST 5 CHUNKS ===")
for i, chunk in enumerate(result["chunks"][:5]):
    print(f"\n--- CHUNK {i} ({len(chunk)} chars, ~{len(chunk)//4} tokens) ---")
    print(chunk[:300] + "..." if len(chunk) > 300 else chunk)

# Output 3: Save full result to JSON for inspection
import json
with open("data/debug_output/pdf_parsing_result.json", "w") as f:
    json.dump({
        "metadata": result["metadata"],
        "sections": {k: len(v) for k, v in result["sections"].items()},
        "sample_chunks": result["chunks"][:3]
    }, f, indent=2)

print(f"\n✓ Full output saved to data/debug_output/pdf_parsing_result.json")
```

**Unit Tests: `tests/test_pdf_ingest.py`**
- Test `extract_text_from_pdf()` returns non-empty string
- Test `detect_sections()` finds "Methods" and "Results"
- Test `chunk_text()` produces chunks in correct token range
- Test `pipeline_pdf_to_chunks()` returns valid metadata

**Acceptance Criteria**:
- [ ] `debug_pdf_ingest.py` runs without errors on test PDF
- [ ] Output shows all detected sections and sample chunks
- [ ] Unit tests pass
- [ ] Debug JSON is human-readable and saved

---

### Task 1.6: Manual Validation & Quality Report
**Owner**: You
**Status**: Pending
**Effort**: 1.5 hours

Manually inspect the pipeline output and document findings.

**Steps**:
1. Run `debug_pdf_ingest.py` on your test PDF
2. Open the PDF in your PDF reader and compare:
   - Are all sections detected correctly?
   - Do the chunks preserve important context?
   - Is any text missing or garbled?
3. Pick 3 chunks and ask yourself: "If I gave this chunk to an LLM with no other context, would it understand it?"
4. Document findings in `SPRINT_1_VALIDATION.md`:

**Template for `SPRINT_1_VALIDATION.md`**:
```markdown
# Sprint 1 Validation Report

## Test PDF
- **Title**: [Title of your paper]
- **Authors**: [Authors]
- **Journal**: [Journal name]
- **Pages**: [N]

## Parsing Results
- **Sections detected**: [list all sections found]
- **Total text length**: [chars]
- **Total tokens**: [est.]
- **Number of chunks**: [N]
- **Avg tokens/chunk**: [N]

## Quality Assessment

### ✅ What Worked
- [e.g., "Methods section cleanly separated"]
- [e.g., "Chunks preserve sentence boundaries"]

### ⚠️ Issues Found
- [e.g., "References section includes author bios"]
- [e.g., "Chunk 23 splits mid-table"]

### 🔧 Improvements for Next Sprint
- [e.g., "Need to filter out References before chunking"]
- [e.g., "Consider lower overlap for dense tables"]

## Conclusion
PDF parsing is [✓ Ready / ⚠️ Needs tweaks] for next phase.
```

**Acceptance Criteria**:
- [ ] Validation report is written and saved
- [ ] Report confirms: sections are accurate, chunks are sensible, no major text loss
- [ ] Any issues are documented with specific examples (chunk numbers, text snippets)
- [ ] Recommendation is clear: proceed to Sprint 2 or iterate on Sprint 1

---

## Acceptance Criteria (Full Sprint)

All tasks complete when:
- [ ] Repo structure matches spec (Task 1.1)
- [ ] Test PDF is sourced and saved (Task 1.2)
- [ ] PDF parser works end-to-end (Task 1.3)
- [ ] Chunking produces valid output (Task 1.4)
- [ ] Debug script runs without errors (Task 1.5)
- [ ] Validation report confirms quality (Task 1.6)
- [ ] Code is committed to git with clear message

---

## Common Pitfalls to Avoid

1. **Don't over-engineer section detection**: Regex is fine. You're not building a full document parser.
2. **Don't skip manual validation**: Run the debug script and actually read 5 chunks. This catches issues early.
3. **Don't ignore text loss**: If 20% of the PDF is missing, stop and debug before moving on.
4. **Don't assume all PDFs parse the same**: Your test PDF might be clean; production PDFs might have scanned images, weird fonts, etc. Make a note of assumptions.

---

## Success Definition

At the end of Sprint 1, you should be able to:
1. **Run one command** (`python debug_pdf_ingest.py data/test_paper.pdf`) and get clean output
2. **Manually inspect** 3–5 chunks and confirm they make sense
3. **Know the failure modes**: What breaks your parser? (Scanned PDFs? Tables? References?)
4. **Move forward confidently** to Sprint 2 knowing your foundation is solid

---

## Next: Sprint 2 Preview

Once Sprint 1 is complete, Sprint 2 will:
- Embed chunks using OpenAI embeddings
- Build a FAISS/Chroma vector store
- Implement RAG retrieval (test: "What was the primary outcome?")
- Validate that top-5 chunks are actually relevant

