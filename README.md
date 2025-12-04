# MGT802_final_project
LLM class website design



One PDF in → RAG-based extraction → structured text abstract + JSON → fixed-template visual abstract rendering.

A. PDF → Text → Chunking Pipeline
Extract text using something simple (e.g., PyPDF, pdfplumber, or pypdf).
Identify rough sections (not sophisticated NLP, just regex like “Methods”, “Results”).
Chunk by fixed size (e.g., 800–1200 tokens).

B. RAG (Retrieval Augmented Generation)
Embed chunks using OpenAI embeddings.
Store embeddings using a simple in-memory vector store (FAISS or Chroma).
For each “task” (PICOT, stats, limitations), retrieve top-k (e.g., 5–8) chunks.

C. LLM-Based Information Extraction (Structured JSON)
Three extraction chains (each is one LLM call):
- PICOT + metadata extraction (Output structured JSON).
- Key numeric result extraction
    -Effect size, CI, p-value, primary endpoint.
    -Limitations extraction
    -Short bullet points from retrieved text.

D. LLM-Based Structured Abstract Generation
    -Input = PICOT + stats JSON
    -Output = structured abstract with four headings:
    -Background
    -Methods
    -Results
    -Conclusions

E. Visual Abstract JSON Specification
NOT dynamic layout generation.
YES: A simple fixed template (boxes like title, population, intervention, comparator, outcomes, limitations).
LLM fills in the content in JSON.

F. Simple Front-End
Use Streamlit (fastest to build/host).
Minimal UI:
-Upload PDF
-Button: “Generate Visual Abstract”
-Output:
    Structured text abstract
    Render boxes using HTML/CSS or Streamlit containers
    Optionally show raw JSON

G. Evaluation (Lightweight but Real)
-5–10 cardiovascular trial PDFs.
-You compare:
    Which extracted numbers match the source text
    Whether any hallucinations occurred
    How close the structured abstract is to the actual published abstract
-Short user feedback from 2–3 colleagues.


H. Technical Report
Should include:
- System architecture
- The 4-step pipeline
- RAG retrieval examples
- Failure cases
- Discussion of limitations
- Short evaluation table

___________________________________________________

[ User Browser ]
       |
       v
[ Streamlit UI (app.py) ]
   - upload PDF
   - "Generate Visual Abstract" button
       |
       v
[ PDF Ingestion Layer ]
   - pdf_ingest.extract_text(pdf_bytes)
   - pdf_ingest.split_into_sections(text)
   - pdf_ingest.chunk_sections(sections)
       |
       v
[ Embedding & Vector Store ]
   - embedder.embed_chunks(chunks)
   - vector_store.index(chunks, embeddings)
       |
       v
[ EvidenceExtractorAgent ]
   (uses RAG + LLM)
   - retrieve_context("picot")        --> LLM Call #1: extract PICOT JSON
   - retrieve_context("stats")        --> LLM Call #2: extract stats JSON
   - retrieve_context("limitations")  --> LLM Call #3: extract limitations JSON
       |
       v
[ AbstractDesignerAgent ]
   (pure LLM transforms)
   - LLM Call #4: structured abstract from {PICOT, stats, limits}
   - LLM Call #5: visual layout JSON from {PICOT, stats, limits}
       |
       v
[ Streamlit UI Rendering ]
   - show structured text abstract
   - render fixed layout boxes using visual layout JSON
   - optional: show raw JSON for debugging

## Quick Setup
- Create a `.env` file with `OPENAI_API_KEY=your_key_here`.
- Install dependencies: `pip install -r requirements.txt`.
- Ensure `data/chroma_db/` exists (Chroma will initialize it on first run).
- Run the Streamlit app: `streamlit run app.py`.
