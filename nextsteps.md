# Next Steps to Complete the Project

- **LLM extraction pipeline**: Implement the agent/prompt layer that runs PDF chunks through PICOT + stats + limitations extraction, then generates (a) structured abstract text and (b) visual abstract JSON. Wire it into `QASystem`/agents instead of placeholder/fallback values.
- **Visual abstract data flow**: Refactor `VisualAbstractGenerator` and `utils/data_extraction.py` to consume real extracted JSON (not hardcoded SELECT trial defaults). Align the Streamlit app questions/inputs with that schema and pass the parsed data through to rendering.
- **Structured abstract UI**: Add a panel in `app.py` to show the generated Background/Methods/Results/Conclusions block alongside the visual abstract.
- **Evaluation tooling**: Add scripts to run the pipeline on multiple PDFs, score numeric extraction accuracy and hallucinations, and produce a short report. Expand `data/papers` with a small benchmark set.
- **Config and deps**: Add `.env.example` with `OPENAI_API_KEY` guidance, document initializing `data/chroma_db`, and update `requirements.txt` to include all used packages (`chromadb`, `numpy`, `pytest`, etc.).
- **Tests and stability**: Fix brittle/incorrect assertions in existing tests, reduce reliance on a single demo JSON, and add an integration test that covers PDF → extraction → abstract → image to catch regressions.

## 2-Week Sprint Plan

### Week 1
- Pipeline: Implement PICOT/stats/limitations extraction prompts and structured abstract generation; wire into `QASystem`.
- Data flow: Refactor `VisualAbstractGenerator` + `utils/data_extraction.py` to consume real JSON schema; update Streamlit to pass parsed data through.
- Dependencies: Add `.env.example`, expand `requirements.txt`, document `data/chroma_db` setup.

### Week 2
- UI/UX: Add structured abstract panel in Streamlit; polish visual abstract options.
- Evaluation: Add benchmark PDFs, write eval script for numeric accuracy/hallucinations, and draft short findings report.
- Testing: Fix brittle tests, add end-to-end integration test (PDF → extraction → abstract → image); ensure pytest runs headless.
