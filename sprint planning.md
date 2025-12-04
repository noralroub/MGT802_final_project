# Visual Abstract Generator - Sprint Planning & User Stories

## 1. USER PERSONAS & JOURNEYS

### Persona 1: Dr. Sarah Chen - Clinical Researcher
- **Role**: Cardiovascular researcher at academic medical center
- **Goals**: Publish findings, share research on social media, increase paper visibility
- **Pain Points**: 
  - Spends 2-3 hours creating visual abstracts manually using PowerPoint
  - Inconsistent formatting across different papers
  - Often misses key methodological details when summarizing
- **Tech Savvy**: Medium (comfortable with web apps, not a programmer)

**Current Journey (Pain Points)**:
1. Reads published paper → manually identifies key elements
2. Opens PowerPoint → creates boxes and layout from scratch
3. Types in information → formats text, adjusts spacing
4. Exports to PNG → posts on Twitter/LinkedIn
5. **Time**: 2-3 hours, **Frustration**: High inconsistency

**Ideal Journey (With Our App)**:
1. Uploads PDF to web app
2. Clicks "Generate Visual Abstract"
3. Reviews generated abstract → makes minor edits if needed
4. Downloads visual abstract
5. **Time**: 5-10 minutes, **Satisfaction**: High accuracy and consistency

---

### Persona 2: Dr. Marcus Rodriguez - Journal Editor
- **Role**: Associate Editor at cardiology journal
- **Goals**: Quickly assess paper quality, create promotional materials for accepted papers
- **Pain Points**:
  - Needs to review 20+ submissions per week
  - Wants standardized visual abstracts for journal's social media
  - Authors submit inconsistent visual abstract formats
- **Tech Savvy**: Medium-High

**Current Journey**:
1. Reads full paper during review process
2. Manually extracts PICOT and key statistics
3. Requests author to create visual abstract post-acceptance
4. **Time**: 30 min per paper + waiting for author, **Frustration**: Delays publication timeline

**Ideal Journey**:
1. Uploads accepted paper PDF
2. Generates standardized visual abstract
3. Shares with authors for verification
4. Publishes immediately
5. **Time**: 5 minutes, **Satisfaction**: Faster publication, consistency

---

### Persona 3: Medical Student Lisa Patel
- **Role**: 3rd year medical student creating journal club presentation
- **Goals**: Understand and present recent cardiovascular trials to peers
- **Pain Points**:
  - Struggles to identify key study parameters (PICOT)
  - Spends hours making presentation slides
  - Misses important limitations or statistical nuances
- **Tech Savvy**: High (digital native)

**Current Journey**:
1. Finds relevant paper → reads 10+ pages
2. Highlights key sections → takes notes
3. Creates PowerPoint slides → formats data
4. **Time**: 3-4 hours per paper, **Frustration**: Often misses important details

**Ideal Journey**:
1. Uploads paper PDF
2. Sees structured abstract with all key elements
3. Uses visual abstract in presentation
4. **Time**: 30 minutes, **Satisfaction**: Comprehensive understanding

---

## 2. PROBLEM VALIDATION

**Evidence This Problem is Real**:
- Personal experience: As someone in the medical field, creating visual abstracts manually is time-consuming
- Academic literature: Visual abstracts increase social media engagement by 2-3x (BMJ study)
- Market demand: Journals increasingly require visual abstracts (JAMA, Circulation, etc.)

**User Pain Points**:
1. **Time-intensive**: 2-3 hours to create one visual abstract manually
2. **Inconsistency**: Each person creates different formats
3. **Errors**: Manual extraction leads to missing key details or misrepresenting statistics
4. **Expertise required**: Need to understand study design to extract PICOT correctly

**Why Existing Solutions Are Insufficient**:
- **PowerPoint/Canva**: Manual, slow, no intelligence
- **Generic summarization tools**: Don't understand clinical trial structure (PICOT, endpoints)
- **PubMed summaries**: Text-only, no visual output, not customized for social media
- **Academic search engines**: Provide abstracts but not visual formats

---

## 3. PRODUCT BACKLOG - USER STORIES (INVEST Format)

### EPIC 1: PDF Processing & Document Ingestion

#### US-001: Upload PDF File
**Priority**: HIGH | **Story Points**: 2

**User Story**: As a clinical researcher, I want to upload a PDF of my published paper, so that the system can extract information from it.

**Acceptance Criteria**:
- **Given** I am on the home page, **When** I click the upload button and select a PDF file, **Then** the file is successfully uploaded and I see a confirmation message
- **Given** I upload a non-PDF file, **When** I click submit, **Then** I see an error message stating "Only PDF files are supported"
- **Given** I upload a PDF larger than 50MB, **When** I click submit, **Then** I see an error message stating file size limits

---

#### US-002: Extract Text from PDF
**Priority**: HIGH | **Story Points**: 5

**User Story**: As a researcher, I want the system to extract text from my PDF accurately, so that subsequent analysis is based on correct content.

**Acceptance Criteria**:
- **Given** a valid PDF is uploaded, **When** text extraction runs, **Then** all text content is extracted with >95% accuracy
- **Given** a PDF with images/tables, **When** extraction runs, **Then** text around images is preserved correctly
- **Given** extraction is complete, **When** I view debug mode, **Then** I can see the extracted raw text

---

#### US-003: Detect Paper Sections
**Priority**: HIGH | **Story Points**: 3

**User Story**: As a system, I want to automatically identify key sections (Introduction, Methods, Results, Discussion), so that I can retrieve relevant chunks for each extraction task.

**Acceptance Criteria**:
- **Given** extracted text, **When** section detection runs, **Then** I can identify at least Methods and Results sections with >80% accuracy
- **Given** non-standard section headers, **When** detection runs, **Then** fallback heuristics are applied (e.g., word patterns, position)
- **Given** sections are detected, **When** displayed in debug view, **Then** I see section boundaries highlighted

---

#### US-004: Chunk Document into Segments
**Priority**: HIGH | **Story Points**: 2

**User Story**: As a system, I want to split the paper into 800-1200 token chunks, so that RAG retrieval is efficient and context fits in LLM calls.

**Acceptance Criteria**:
- **Given** extracted text, **When** chunking runs, **Then** chunks are between 800-1200 tokens each
- **Given** a section boundary exists, **When** chunking, **Then** chunks do not split mid-sentence
- **Given** chunks are created, **When** I view metadata, **Then** each chunk is labeled with its source section

---

### EPIC 2: RAG (Retrieval Augmented Generation)

#### US-005: Embed Document Chunks
**Priority**: HIGH | **Story Points**: 3

**User Story**: As a system, I want to create vector embeddings for each chunk, so that I can retrieve relevant sections during information extraction.

**Acceptance Criteria**:
- **Given** document chunks, **When** embedding process runs, **Then** all chunks are embedded using OpenAI embeddings API
- **Given** embeddings are created, **When** stored in vector DB, **Then** I can query the DB successfully
- **Given** embedding fails for a chunk, **When** error occurs, **Then** system logs error and continues with other chunks

---

#### US-006: Store Embeddings in Vector Database
**Priority**: HIGH | **Story Points**: 3

**User Story**: As a system, I want to store embeddings in an in-memory FAISS/Chroma database, so that retrieval is fast during generation.

**Acceptance Criteria**:
- **Given** embeddings are created, **When** storage runs, **Then** all embeddings are stored in FAISS with <2 second latency
- **Given** database is initialized, **When** I query with a sample question, **Then** I retrieve top-k most relevant chunks
- **Given** session ends, **When** user leaves, **Then** in-memory database is cleared (no persistence)

---

#### US-007: Retrieve Relevant Chunks by Query
**Priority**: HIGH | **Story Points**: 2

**User Story**: As a system, I want to retrieve the top-k most relevant chunks given a query, so that LLM calls are grounded in source text.

**Acceptance Criteria**:
- **Given** a query like "What is the study population?", **When** retrieval runs, **Then** top 5-8 chunks from Methods section are returned
- **Given** retrieved chunks, **When** displayed, **Then** similarity scores are shown for each chunk
- **Given** no relevant chunks exist, **When** retrieval runs, **Then** system returns a warning message

---

### EPIC 3: Information Extraction (LLM Calls 1-3)

#### US-008: Extract PICOT Elements
**Priority**: HIGH | **Story Points**: 5

**User Story**: As a researcher, I want the system to extract Population, Intervention, Comparator, Outcomes, and Timeframe, so that I understand the study design at a glance.

**Acceptance Criteria**:
- **Given** relevant chunks are retrieved, **When** PICOT extraction runs, **Then** I receive structured JSON with all 5 PICOT elements filled
- **Given** PICOT JSON is returned, **When** I view results, **Then** each field contains accurate information from the source paper
- **Given** a field cannot be determined, **When** extraction runs, **Then** that field is marked as "Not specified" rather than hallucinated

---

#### US-009: Extract Study Design Metadata
**Priority**: MEDIUM | **Story Points**: 3

**User Story**: As a journal editor, I want to see the study design type (RCT, cohort, case-control, etc.), so that I can quickly assess the evidence level.

**Acceptance Criteria**:
- **Given** PICOT extraction runs, **When** metadata is extracted, **Then** study design is correctly identified (e.g., "Randomized Controlled Trial")
- **Given** study design is identified, **When** displayed, **Then** it is shown alongside PICOT elements
- **Given** design is ambiguous, **When** extraction runs, **Then** system provides the most likely design with confidence score

---

#### US-010: Extract Key Statistics and Effect Sizes
**Priority**: HIGH | **Story Points**: 5

**User Story**: As a researcher, I want the system to extract primary outcomes, effect sizes, confidence intervals, and p-values, so that I can see the quantitative results quickly.

**Acceptance Criteria**:
- **Given** Results section chunks, **When** statistics extraction runs, **Then** I receive JSON with primary endpoint, effect size (HR/OR/RR), 95% CI, and p-value
- **Given** multiple outcomes are reported, **When** extraction runs, **Then** system prioritizes primary outcome over secondary outcomes
- **Given** statistics are complex, **When** extraction runs, **Then** system includes units and context (e.g., "HR 0.75 for all-cause mortality")

---

#### US-011: Extract Sample Size and Follow-up Duration
**Priority**: MEDIUM | **Story Points**: 2

**User Story**: As a medical student, I want to see the sample size and follow-up duration, so that I can assess the study's power and validity.

**Acceptance Criteria**:
- **Given** Methods section chunks, **When** extraction runs, **Then** total sample size (n) is extracted and displayed
- **Given** follow-up duration exists, **When** extraction runs, **Then** median/mean follow-up time is extracted (e.g., "24 months")
- **Given** dropout rates are mentioned, **When** extraction runs, **Then** they are included in the output

---

#### US-012: Extract Study Limitations
**Priority**: MEDIUM | **Story Points**: 3

**User Story**: As a researcher, I want to see 3-5 key study limitations, so that I can understand potential biases or generalizability concerns.

**Acceptance Criteria**:
- **Given** Discussion section chunks, **When** limitations extraction runs, **Then** I receive 3-5 concise bullet points of limitations
- **Given** limitations are extracted, **When** displayed, **Then** they are in plain language without jargon where possible
- **Given** no explicit limitations section exists, **When** extraction runs, **Then** system searches Discussion for phrases like "limitation", "weakness", etc.

---

### EPIC 4: Structured Abstract Generation (LLM Call 4)

#### US-013: Generate Structured Text Abstract
**Priority**: HIGH | **Story Points**: 5

**User Story**: As a researcher, I want a 4-section structured abstract (Background, Methods, Results, Conclusions), so that I have a concise summary ready to share.

**Acceptance Criteria**:
- **Given** PICOT, stats, and limitations JSON, **When** abstract generation runs, **Then** I receive a structured abstract with exactly 4 sections
- **Given** each section is generated, **When** I view output, **Then** Background is 2-3 sentences, Methods is 3-4 sentences, Results is 3-4 sentences, Conclusions is 2-3 sentences
- **Given** abstract is generated, **When** I compare to source paper, **Then** no hallucinated facts are present (all claims grounded in retrieved chunks)

---

#### US-014: Validate Abstract Against Source Text
**Priority**: MEDIUM | **Story Points**: 3

**User Story**: As a system, I want to validate that numerical claims in the abstract match the source paper, so that accuracy is maintained.

**Acceptance Criteria**:
- **Given** abstract contains numbers, **When** validation runs, **Then** each number is checked against retrieved chunks
- **Given** a number doesn't match source, **When** validation detects this, **Then** a warning flag is displayed to the user
- **Given** validation passes, **When** displayed, **Then** user sees a "Validated ✓" badge

---

### EPIC 5: Visual Abstract Generation (LLM Call 5 + Rendering)

#### US-015: Generate Visual Abstract JSON Specification
**Priority**: HIGH | **Story Points**: 5

**User Story**: As a researcher, I want the system to create a JSON specification for a visual abstract, so that I can render it as a shareable image.

**Acceptance Criteria**:
- **Given** extracted JSON from previous steps, **When** visual spec generation runs, **Then** I receive JSON with 7 fixed boxes (Title, Population, Intervention, Comparator, Outcomes, Key Results, Limitations)
- **Given** visual JSON is generated, **When** I view it, **Then** each box contains concise, readable text (<50 words per box)
- **Given** key results include numbers, **When** spec is generated, **Then** numbers are prominently displayed (e.g., "↓ 25% risk reduction")

---

#### US-016: Render Visual Abstract as HTML/CSS
**Priority**: HIGH | **Story Points**: 5

**User Story**: As a researcher, I want to see the visual abstract rendered as a clean, colorful layout, so that I can use it in presentations or social media.

**Acceptance Criteria**:
- **Given** visual JSON spec, **When** rendering runs, **Then** I see a grid layout with 7 labeled boxes displayed in the Streamlit app
- **Given** rendering is complete, **When** I view output, **Then** boxes have distinct colors, readable fonts (minimum 14pt), and clear hierarchy
- **Given** I want to save the visual, **When** I click download, **Then** I can export as PNG or HTML

---

#### US-017: Apply Cardiovascular-Themed Styling
**Priority**: LOW | **Story Points**: 2

**User Story**: As a cardiologist, I want the visual abstract to have a cardiovascular theme (heart icons, red/blue color scheme), so that it's visually appealing for my field.

**Acceptance Criteria**:
- **Given** rendering runs, **When** I view visual abstract, **Then** I see heart or ECG icon in the title box
- **Given** color scheme is applied, **When** displayed, **Then** intervention box is red, comparator is blue, outcomes are green
- **Given** I don't like the theme, **When** I toggle setting, **Then** I can switch to a neutral theme

---

### EPIC 6: User Interface & Experience

#### US-018: Display Processing Progress
**Priority**: MEDIUM | **Story Points**: 3

**User Story**: As a user, I want to see real-time progress as my paper is processed, so that I know the system is working and how long to wait.

**Acceptance Criteria**:
- **Given** I upload a PDF, **When** processing starts, **Then** I see a progress bar with steps (Parsing → Embedding → Extracting → Generating)
- **Given** each step completes, **When** displayed, **Then** step is marked with a checkmark and estimated time remaining is shown
- **Given** an error occurs, **When** detected, **Then** progress bar turns red and error message is displayed

---

#### US-019: View Raw Extracted JSON
**Priority**: LOW | **Story Points**: 2

**User Story**: As a power user, I want to toggle a "Show JSON" view, so that I can see the raw extracted data and use it for other purposes.

**Acceptance Criteria**:
- **Given** I click "Show JSON" toggle, **When** activated, **Then** I see collapsible sections for PICOT JSON, Stats JSON, Limitations JSON, and Visual JSON
- **Given** JSON is displayed, **When** I click "Copy" button, **Then** JSON is copied to my clipboard
- **Given** I want to hide JSON, **When** I toggle off, **Then** JSON view is hidden and only visual/text abstracts are shown

---

#### US-020: Download Text Abstract as Plain Text
**Priority**: MEDIUM | **Story Points**: 1

**User Story**: As a researcher, I want to download the structured text abstract as a .txt file, so that I can paste it into emails or documents.

**Acceptance Criteria**:
- **Given** abstract is generated, **When** I click "Download Text Abstract", **Then** a .txt file is downloaded with the 4-section abstract
- **Given** file is opened, **When** I view it, **Then** sections are clearly labeled with headers
- **Given** I want to copy inline, **When** I click "Copy to Clipboard", **Then** abstract is copied without needing to download

---

### EPIC 7: Error Handling & Validation

#### US-021: Handle Invalid PDFs Gracefully
**Priority**: HIGH | **Story Points**: 2

**User Story**: As a user, I want clear error messages when my PDF can't be processed, so that I understand what went wrong and can fix it.

**Acceptance Criteria**:
- **Given** I upload a corrupted PDF, **When** parsing fails, **Then** I see message "Unable to extract text from PDF. Please ensure file is not password-protected or corrupted."
- **Given** PDF is scanned images only, **When** text extraction finds no text, **Then** I see message "This PDF appears to be scanned images. OCR is not yet supported."
- **Given** error occurs, **When** displayed, **Then** I am returned to upload screen to try again

---

#### US-022: Retry Failed LLM Calls
**Priority**: MEDIUM | **Story Points**: 3

**User Story**: As a system, I want to automatically retry failed LLM API calls up to 3 times, so that transient errors don't break the pipeline.

**Acceptance Criteria**:
- **Given** an LLM call fails (timeout, rate limit), **When** error occurs, **Then** system waits 2 seconds and retries
- **Given** retry succeeds, **When** processing continues, **Then** user is unaware of the failure (seamless experience)
- **Given** all 3 retries fail, **When** this happens, **Then** user sees error message with option to "Try Again" or "Report Issue"

---

---

## 4. STORY POINT SUMMARY

**Total Story Points**: 70 points

**Breakdown by Epic**:
- EPIC 1 (PDF Processing): 12 points
- EPIC 2 (RAG): 8 points
- EPIC 3 (Extraction): 18 points
- EPIC 4 (Abstract Generation): 8 points
- EPIC 5 (Visual Generation): 12 points
- EPIC 6 (UI/UX): 6 points
- EPIC 7 (Error Handling): 5 points

**Priority Breakdown**:
- HIGH: 45 points (15 user stories)
- MEDIUM: 20 points (6 user stories)
- LOW: 4 points (2 user stories)

---

## 5. SPRINT 2 PLAN (Days 1-3)

**Sprint Goal**: "Build a functional pipeline from PDF upload to structured text abstract"

**Duration**: 3 days (Dec 5-7, 2025)

**Team Capacity**: 25 story points (assuming solo work, ~8-10 hours/day)

### Selected User Stories:

| ID | Title | Priority | Story Points | Status |
|---|---|---|---|---|
| US-001 | Upload PDF File | HIGH | 2 | To Do |
| US-002 | Extract Text from PDF | HIGH | 5 | To Do |
| US-003 | Detect Paper Sections | HIGH | 3 | To Do |
| US-004 | Chunk Document | HIGH | 2 | To Do |
| US-005 | Embed Document Chunks | HIGH | 3 | To Do |
| US-006 | Store Embeddings in Vector DB | HIGH | 3 | To Do |
| US-007 | Retrieve Relevant Chunks | HIGH | 2 | To Do |
| US-008 | Extract PICOT Elements | HIGH | 5 | To Do |

**Total Committed: 25 Story Points**

### Dependencies:
- US-002 must complete before US-003
- US-003 must complete before US-004
- US-004 must complete before US-005
- US-005 must complete before US-006
- US-006 must complete before US-007
- US-007 must complete before US-008

### Risks:
1. **PDF parsing complexity**: Some cardiovascular papers have complex tables/figures that may break extraction
   - *Mitigation*: Test with 3 sample PDFs early, fallback to simpler parsing if needed
2. **RAG retrieval accuracy**: May retrieve irrelevant chunks
   - *Mitigation*: Use section labels to constrain retrieval (e.g., only search Methods for PICOT)
3. **LLM API rate limits**: OpenAI free tier may throttle
   - *Mitigation*: Use exponential backoff, implement retry logic (US-022)

### Definition of Done for Sprint 2:
- [ ] User can upload a PDF and see extracted text
- [ ] System can detect Methods and Results sections
- [ ] RAG retrieval returns relevant chunks for PICOT query
- [ ] PICOT extraction returns valid JSON for 1 test paper
- [ ] All code has docstrings and type hints
- [ ] Unit tests for pdf_processor.py and rag_retriever.py

---

## 6. SPRINT 3 PLAN (Days 4-5)

**Sprint Goal**: "Complete MVP with visual abstract generation and deploy to Streamlit Cloud"

**Duration**: 2 days (Dec 8-9, 2025)

**Team Capacity**: 18 story points

### Selected User Stories:

| ID | Title | Priority | Story Points | Status |
|---|---|---|---|---|
| US-010 | Extract Key Statistics | HIGH | 5 | To Do |
| US-012 | Extract Study Limitations | MEDIUM | 3 | To Do |
| US-013 | Generate Structured Text Abstract | HIGH | 5 | To Do |
| US-015 | Generate Visual Abstract JSON | HIGH | 5 | To Do |
| US-016 | Render Visual Abstract HTML/CSS | HIGH | 5 | To Do |
| US-018 | Display Processing Progress | MEDIUM | 3 | To Do |

**Total Committed: 26 Story Points** *(slight overcommit, can cut US-018 if needed)*

### Dependencies:
- US-010, US-012 depend on US-007 (retrieval working)
- US-013 depends on US-008, US-010, US-012
- US-015 depends on US-008, US-010, US-012
- US-016 depends on US-015

### Risks:
1. **Visual rendering complexity**: HTML/CSS layout may be harder than expected
   - *Mitigation*: Use simple CSS Grid, avoid complex positioning
2. **Deployment issues**: Streamlit Cloud may have dependency conflicts
   - *Mitigation*: Test deployment on Day 4 afternoon, not last minute

### Definition of Done for Sprint 3:
- [ ] User can generate complete visual abstract from PDF
- [ ] Visual abstract renders correctly in Streamlit
- [ ] App is deployed to Streamlit Cloud and accessible via URL
- [ ] README.md includes setup instructions and demo link
- [ ] Evaluation script runs on 5 test papers

---

## 7. NICE-TO-HAVE (Post-MVP / Future Sprints)

**Deferred User Stories** (30+ story points):
- US-009: Extract Study Design Metadata (3 pts)
- US-011: Extract Sample Size and Follow-up (2 pts)
- US-014: Validate Abstract Against Source (3 pts)
- US-017: Apply Cardiovascular Styling (2 pts)
- US-019: View Raw JSON (2 pts)
- US-020: Download Text Abstract (1 pt)
- US-021: Handle Invalid PDFs (2 pts)
- US-022: Retry Failed LLM Calls (3 pts)

**Future Enhancements** (Not in current backlog):
- PubMed ID support
- Multi-language support
- Custom visual templates
- User accounts and saved abstracts
- Batch processing multiple PDFs

---

## 8. TECHNICAL ARCHITECTURE DECISIONS

### Backend Framework
**Choice**: Python + Streamlit
**Rationale**: 
- Fastest to deploy (built-in UI components)
- Native Python ecosystem for LLM/RAG tools
- Free hosting on Streamlit Cloud
- No need for separate frontend/backend

### Database
**Choice**: FAISS (in-memory vector store)
**Rationale**:
- No persistence needed (fresh vectors per session)
- Faster than ChromaDB for small datasets (<100 chunks)
- Zero configuration, no external dependencies

### LLM Provider
**Choice**: OpenAI API (GPT-4 for extraction, GPT-3.5 for generation)
**Rationale**:
- Most reliable structured output (JSON mode)
- Good balance of cost vs. accuracy
- Fallback: Claude API if needed

### Deployment Platform
**Choice**: Streamlit Cloud (free tier)
**Rationale**:
- Direct GitHub integration
- Automatic deploys on push
- Handles HTTPS/SSL automatically
- 1GB RAM sufficient for our use case

### Development Workflow
- **Branching Strategy**: Feature branches (`feature/US-XXX-description`)
- **Code Review**: Self-review since solo project (document decisions in commit messages)
- **CI/CD**: GitHub Actions for linting (optional if time permits)

---

## 9. EVALUATION PLAN

### Quantitative Metrics (5-10 Test Papers):

1. **Factual Accuracy**:
   - Compare extracted numbers (HR, CI, p-values) to source paper
   - Target: 100% match (no hallucinations)

2. **PICOT Completeness**:
   - Check if all 5 PICOT elements are extracted when present in paper
   - Target: >90% recall

3. **Processing Time**:
   - Measure end-to-end time from upload to visual abstract
   - Target: <60 seconds per paper

### Qualitative Evaluation (2-3 Colleagues):

1. **Clarity**: "Is the visual abstract easy to understand?"
2. **Usefulness**: "Would you use this tool for your own papers?"
3. **Accuracy**: "Does the abstract accurately represent the study?"

**Evaluation Deliverable**: CSV file with results + 1-page summary in technical report

---

## NEXT STEPS

1. **Set up GitHub Project with these user stories**
2. **Create issue templates** (.github/ISSUE_TEMPLATE/)
3. **Document Definition of Ready and Definition of Done**
4. **Begin Sprint 2** (start with US-001: Upload PDF)
5. **Daily check-ins** (solo: end-of-day review of progress vs. plan)

---

**Document Version**: 1.0  
**Last Updated**: December 4, 2025  
**Project**: Visual Abstract Generator for Cardiovascular Clinical Trials  
**Timeline**: December 5-9, 2025 (5 days)