Automated Visual Abstract Generator

A lightweight RAG-powered system for extracting structured insights from scientific papers and generating visual abstracts.

📌 Project Overview

Researchers and clinicians increasingly rely on visual abstracts to quickly understand and share key findings from new scientific papers. But creating these visuals is time-consuming, inconsistent, and often omits important methodological details.

This project builds a simple, end-to-end prototype that:

Ingests a scientific PDF (focused on cardiovascular clinical trials)

Extracts key structured information using Retrieval-Augmented Generation (RAG)

Generates two outputs:

A structured written abstract (Background, Methods, Results, Conclusions)

A JSON-based visual abstract layout that populates a fixed template of boxes

The entire pipeline is intentionally minimal and optimized for a ~4–5 day build.

🧩 System Architecture

The pipeline follows a clean sequence of steps:

PDF Ingestion & Section Parsing

Extract raw text

Identify rough sections (e.g., Methods, Results)

Chunk text for retrieval

Vector Store & Embeddings

Convert chunks to embeddings using OpenAI

Store in FAISS/Chroma for efficient retrieval

Evidence Extraction (LLM + RAG)

Retrieve relevant chunks to extract:

PICOT (Population, Intervention, Comparator, Outcomes, Timing)

Key numeric results (effect sizes, CIs, p-values)

Study limitations

Abstract Designer (LLM)

Generate a structured text abstract from extracted JSON

Generate a JSON specification for a fixed visual abstract template

Streamlit UI

Upload PDF

Display structured abstract

Render visual abstract layout using simple boxes

Optionally show raw JSON outputs

A more detailed diagram is included in /docs/architecture.png (or adjust if you want).

📁 Repository Structure
project/
│
├── app.py                         # Streamlit frontend
├── config.py                      # API keys, model names, constants
│
├── core/
│   ├── pdf_ingest.py             # PDF → text → sections → chunks
│   ├── embeddings.py             # Embedding helper functions
│   └── vector_store.py           # Build and query FAISS/Chroma index
│
├── agents/
│   ├── evidence_extractor.py     # PICOT, stats, limitations (LLM Calls 1–3)
│   └── abstract_designer.py      # Structured abstract + layout JSON (LLM Calls 4–5)
│
├── pipeline/
│   └── visual_abstract_pipeline.py   # Orchestrates end-to-end workflow
│
├── evaluation/
│   └── eval_utils.py             # Factuality checking, comparison tools
│
└── README.md                     # ← You are here

🚀 How to Run
1. Install dependencies
pip install -r requirements.txt

2. Set your OpenAI API key

Create a .env file or export directly:

export OPENAI_API_KEY="your-key-here"

3. Launch the app
streamlit run app.py

4. Upload a PDF

The system will:

Parse the file

Extract structured study information

Generate a textual abstract

Render a visual abstract layout

✨ Features
Implemented

PDF ingestion and section parsing

Chunking + embeddings + vector store

RAG-driven extraction of PICOT, results, limitations

Structured abstract generation

JSON-based visual abstract template generation

Clean Streamlit UI for demos

Light evaluation of factual correctness and clarity

🚫 Out of Scope (Intentionally Excluded)

To keep the project realistic and prevent scope creep, we are NOT doing:

1. Dynamic graphic design or free-form visual layouts

No arrows, icons, or auto-generated images.
All visuals use a fixed template rendered as simple boxes.

2. PubMed or external API ingestion

PDF upload ONLY. No PubMed parsing or scraping.

3. Table or figure extraction

The system extracts information ONLY from text chunks.

4. Multi-step agent frameworks (CrewAI, AutoGen, LangGraph)

We simulate "agents" using simple Python functions and LLM calls.

5. Production backend features

No database, user accounts, async queues, caching layers, or multi-user support.

6. Generalization to all paper types

Prototype is focused on cardiovascular clinical trials for consistency.

🧪 Evaluation Plan

We evaluate the system on a small set of 5–10 papers:

Factuality check: Ensure each extracted number appears in retrieved text.

Quality check: Compare AI abstract to published abstract.

User feedback: Gather clarity + usefulness ratings.

Failure analysis: Highlight hallucinations, missing details, or ambiguity.

📉 Limitations

Extraction accuracy depends on chunk quality and paper formatting

Complex tables/figures are not parsed

The system does not verify statistical correctness

Visual layout is not dynamically optimized—content may overflow

📚 Future Work

Potential next steps (not included in this build):

Dynamic graph or icon rendering

Figure/table parsing

PubMed ID ingestion

Multi-paper batch processing

Domain-specific prompt optimization

Integration with journal workflows