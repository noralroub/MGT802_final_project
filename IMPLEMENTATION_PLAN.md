# Medical Visual Abstract Generator - Implementation Plan

## Overview
This document outlines the strategic approach to address three critical issues:
1. Rigid template that doesn't allow user editing
2. Field population problems due to trial diversity and hardcoded assumptions
3. Hallucination in extracted summaries

## Problem Analysis

### Root Cause
The current architecture has a **backwards data flow**: the template drives data extraction, rather than data extraction informing the template. This creates:
- Hard-coded assumptions about trial structure (Semaglutide-specific patterns)
- Fixed schemas that don't adapt to different trial types
- No validation against paper reality

### Current Limitations
- **[data_extraction.py:179-183](file:///Users/Noralroub/MGT802_final_project/utils/data_extraction.py#L179-L183)**: Hardcoded trial metadata (title, drug, indication, trial_name)
- **[data_extraction.py:15-52](file:///Users/Noralroub/MGT802_final_project/utils/data_extraction.py#L15-L52)**: Regex patterns are Semaglutide-specific (weight changes, GI events, discontinuation)
- **[extraction_agent.py:164-174](file:///Users/Noralroub/MGT802_final_project/agents/extraction_agent.py#L164-L174)**: Fixed `visual_data` schema assumes specific outcomes exist
- **UI**: Read-only display with no editing capability

---

## Solution Architecture

### Phase 1: Editable UI (Priority 1 - Quick Win)
**Goal**: Allow users to edit template fields directly
**Timeline**: 2-4 hours
**Status**: Not started

#### Changes Required
1. **[app.py](file:///Users/Noralroub/MGT802_final_project/app.py) - Tab 3 "Visual Abstract"**
   - Add "Edit Abstract Fields" section
   - Convert static displays to editable forms:
     - `st.text_input()` for trial_info fields (title, drug, indication, trial_name, publication)
     - `st.number_input()` for population fields (total_enrolled, arm sizes, mean age)
     - `st.text_area()` for outcome descriptions
     - `st.slider()` for event rate percentages
   - Add "Save Changes" button to update preview

2. **[ui/visual_template.py](file:///Users/Noralroub/MGT802_final_project/ui/visual_template.py)**
   - Make `render_visual_abstract_from_trial()` accept user-edited data
   - Implement live preview updates as fields change

#### Benefits
- Users can immediately correct extraction errors
- Unblocks users while deeper refactoring happens
- Validates what *should* be in the abstract
- Gives you real examples of how users want to interact with the data

#### Success Criteria
- [ ] All visual abstract fields are editable
- [ ] Changes update preview in real-time
- [ ] Edited data can be exported/saved
- [ ] Users can toggle between "auto-extracted" and "manual-edited" views

---

### Phase 2: Flexible Field Population (Priority 2 - Core Issue)
**Goal**: Make extraction agnostic to trial type
**Timeline**: 8-12 hours
**Status**: Not started

#### 2.1 Add Trial Classification Step (NEW)
**File**: Create `agents/trial_classifier.py`

```python
class TrialClassifier:
    """Classify trial type and extract design metadata."""

    def classify_trial_type(pdf_context: str) -> TrialMetadata:
        """
        Determine:
        - Type: RCT, observational, crossover, cohort, pharmacokinetic, etc.
        - Design: parallel, crossover, factorial, etc.
        - Arms: number, labels, sizes
        - Primary/secondary outcomes: what they are, not assumptions
        - Endpoints: safety, efficacy, pharmacokinetic, etc.
        """
```

This tells you what fields *should* exist before trying to populate them.

#### 2.2 Refactor Outcome Extraction (REFACTOR)
**File**: Modify `agents/extraction_agent.py`

Current approach:
```python
# Assumes specific outcomes
"primary_outcome": {"label": "...", "effect_measure": "...", "estimate": "..."}
"event_rates": {"arm_1_percent": null, "arm_2_percent": null}
"adverse_events": {"summary": "...", "notable": [...]}
```

New approach:
```python
# Generic, flexible structure
"primary_outcomes": [
    {
        "name": "...",
        "measure_type": "hazard_ratio|odds_ratio|mean_difference|event_rate|...",
        "estimate": {"value": null, "units": ""},
        "confidence_interval": {"lower": null, "upper": null},
        "p_value": null,
        "units": "...",
    }
]
"secondary_outcomes": [...]
"safety_data": [
    {"event_name": "...", "arm_1_percent": null, "arm_2_percent": null, ...}
]
```

#### 2.3 Create Dynamic Schema (NEW)
**File**: Create `schemas/trial_schemas.py`

Define flexible data structures:
```python
@dataclass
class TrialOutcome:
    """Generic outcome structure."""
    name: str
    measure_type: str  # hazard_ratio, odds_ratio, mean_difference, event_rate
    estimate: float | None
    confidence_interval: tuple | None
    p_value: float | None
    units: str | None
    population_denominator: int | None

@dataclass
class TrialArm:
    """Trial arm definition."""
    label: str
    size: int | None
    description: str | None

@dataclass
class ClinicalTrial:
    """Flexible trial structure."""
    trial_info: TrialInfo
    design: TrialDesign
    population: TrialPopulation
    arms: list[TrialArm]
    primary_outcomes: list[TrialOutcome]
    secondary_outcomes: list[TrialOutcome]
    safety: SafetyData
    dosing: DosingInfo | None
```

#### 2.4 Update Data Extraction (REFACTOR)
**File**: Replace `utils/data_extraction.py`

- Remove hardcoded Semaglutide patterns
- Add generic outcome extraction:
  - Extract all outcomes mentioned (regardless of type)
  - For each outcome, extract: name, estimate, CI, p-value, units
  - Use structured prompts instead of regex
- Extract safety data as a list, not specific categories
- Make trial_info user-selectable or extracted from paper metadata

#### Benefits
- **Works with ANY trial type** (cardiovascular, oncology, psychiatric, pharmacokinetic)
- **Captures all outcomes**, not just expected ones
- **Prevents data loss** from forcing papers into a template
- **Scalable**: Adding new trial types requires no code changes

#### Success Criteria
- [ ] Trial classifier determines trial type accurately
- [ ] Extraction agent returns flexible schema for diverse trial types
- [ ] No hardcoded trial metadata
- [ ] Extraction works on Semaglutide trial AND other trial types
- [ ] Schema accommodates 1-N outcomes and arms

---

### Phase 3: Visual Template Adaptation (ENHANCEMENT)
**Goal**: Template renders differently based on available data
**Timeline**: 4-6 hours
**Status**: Not started (depends on Phase 2)

#### 3.1 Adaptive Template Rendering
**File**: Modify `core/visual_abstract.py` and `ui/visual_template.py`

Current approach:
```
Always render: header, hero, left_column, right_column, results_box, chart, footer
```

New approach:
```
Based on data available:
- 1 primary outcome → large, prominent display
- 3+ primary outcomes → carousel or multiple cards
- No secondary outcomes → don't render section
- 2+ safety events → render comparison chart
- Adjust spacing and layout to fit content
```

#### Implementation
- Query available data fields
- Choose layout variant (compact, standard, detailed)
- Render only sections with data
- Distribute space proportionally

#### Benefits
- Visual abstract looks professional regardless of trial complexity
- No blank sections or "n/a" clutter
- Better use of space for complex trials
- Simpler for simple trials

#### Success Criteria
- [ ] Template adapts to 1, 2, or 3+ primary outcomes
- [ ] Safety events render as charts when multiple types present
- [ ] No rendering of empty sections
- [ ] Layout maintains professional appearance at all data densities

---

### Phase 4: Reduce Hallucination (Quality)
**Goal**: Detect and minimize LLM hallucinations
**Timeline**: 6-8 hours
**Status**: Not started (depends on Phase 2)

#### 4.1 Add Extraction Chains (NEW)
**File**: Create `agents/validation_chains.py`

Implement specialized chains:

```python
class ExtractionChain:
    """Chain to extract and validate facts from text."""

    def extract_and_cite(section: str, query: str) -> list[Fact]:
        """
        Extract facts and return with source citations.
        Returns: [{"value": "...", "confidence": "high|medium|low", "source": "..."}]
        """

    def verify_numbers(numbers: list[float], context: str) -> list[VerificationResult]:
        """Verify extracted numbers appear in original text."""

    def check_contradictions(facts: list[Fact]) -> list[Contradiction]:
        """Detect inconsistencies in reported values."""
```

#### 4.2 Citation Tracking (NEW)
**File**: Modify `agents/extraction_agent.py`

For every extracted data point, store:
```python
@dataclass
class FactWithCitation:
    value: str | float
    confidence: str  # high, medium, low
    source_chunk: str  # Text from PDF
    source_page: int | None
    extracted_by: str  # Which chain/prompt
```
```

Update schema to include citations:
```python
"primary_outcomes": [
    {
        "name": "Serious adverse events",
        "estimate": 6.5,
        "units": "%",
        "confidence": "high",
        "source_chunk": "In the semaglutide group, 6.5% of patients...",
        "source_page": 5,
    }
]
```

#### 4.3 Confidence Scoring (NEW)
**File**: Modify `agents/extraction_agent.py`

Have extraction agent return confidence for each field:
- **High**: Exact numbers found in text, appears multiple times
- **Medium**: Inferred from context, derived value
- **Low**: Not found in text, filled with default

#### 4.4 UI Integration (ENHANCEMENT)
**File**: Modify `app.py` tab 3

Display confidence visually:
```
✅ PRIMARY OUTCOME (high confidence)
   Name: Serious adverse events
   Estimate: 6.5% [cite page 5]  ← clickable, shows source

⚠️ BODY WEIGHT CHANGE (medium confidence)
   Change: -9.4%
   (Inferred from text, not explicitly stated)

❓ SECONDARY OUTCOME 1 (low confidence)
   [MISSING - Not found in paper]
```

#### Benefits
- Users immediately see which values might be hallucinated (low confidence)
- Citations prove data came from the paper
- Contradictions are flagged for review
- Builds trust in the system

#### Success Criteria
- [ ] All extracted values have citations
- [ ] Confidence scores assigned correctly
- [ ] Contradictions detected and highlighted
- [ ] Users can click to see source text
- [ ] Low-confidence values are visually marked

---

## Implementation Roadmap

### Week 1: Quick Wins
**Goal**: Make template editable immediately
**Tasks**:
- [ ] Add editable form fields to Visual Abstract tab
- [ ] Implement live preview updates
- [ ] Save/export edited abstracts
- [ ] Deploy and get user feedback

**Deliverable**: Users can now fix extraction errors manually

---

### Week 2-3: Core Refactor
**Goal**: Make extraction flexible and trial-agnostic
**Tasks**:
- [ ] Design flexible data schemas (`schemas/trial_schemas.py`)
- [ ] Implement trial classifier (`agents/trial_classifier.py`)
- [ ] Refactor extraction agent to use generic outcome extraction
- [ ] Replace regex-based extraction with LLM-based extraction
- [ ] Remove hardcoded Semaglutide assumptions

**Deliverable**: Extraction works on diverse trial types

---

### Week 4: Enhancement & Quality
**Goal**: Make visuals adaptive and extraction trustworthy
**Tasks**:
- [ ] Implement template adaptation logic
- [ ] Add extraction chains with citation tracking
- [ ] Implement confidence scoring
- [ ] Add contradiction detection
- [ ] Update UI to show confidence and citations
- [ ] Test on 5+ different trial types

**Deliverable**: Production-ready system with hallucination detection

---

## Architectural Changes Summary

| Component | Current | Proposed |
|-----------|---------|----------|
| **Data Schema** | Fixed fields (trial_info, population, primary_outcome, ...) | Dynamic fields based on trial type + user selection |
| **Extraction** | Regex patterns + LLM for specific fields | Trial classifier → Flexible LLM extraction → User mapping |
| **Trial Assumptions** | Hardcoded (Semaglutide trial) | Auto-detected from paper |
| **UI** | Read-only display | Display + Edit + Validate + Cite |
| **Outcomes** | Primary/secondary (fixed) | N primary + N secondary (flexible) |
| **Safety Data** | Hardcoded categories | N safety events (flexible) |
| **Hallucination Control** | None | Citations + confidence scores + contradiction checking |
| **Template** | Fixed layout | Adaptive (fits content) |

---

## Key Files to Create/Modify

### New Files (Phase 2-4)
- `schemas/trial_schemas.py` — Flexible data structures
- `agents/trial_classifier.py` — Classify trial type and design
- `agents/validation_chains.py` — Extraction validation and citation chains
- `utils/schema_mapper.py` — Map flexible schema to visual abstract

### Modified Files
- `app.py` — Add editable fields (Phase 1), integrate classifier (Phase 2), show confidence (Phase 4)
- `agents/extraction_agent.py` — Add trial classifier step, update schemas, add citations
- `utils/data_extraction.py` — Replace with generic extraction
- `core/visual_abstract.py` — Add adaptive rendering
- `ui/visual_template.py` — Update to accept flexible schema

### Deprecated Files
- May deprecate hardcoded regex patterns in `utils/data_extraction.py`

---

## Testing Strategy

### Phase 1 Testing
- Manual testing with Semaglutide trial
- Verify fields update preview in real-time
- Test export/save functionality

### Phase 2 Testing
- Test on 5+ different trial types:
  - Cardiovascular (current: Semaglutide)
  - Oncology (different outcomes: tumor response, survival)
  - Psychiatric (different safety: behavioral events)
  - Pharmacokinetic (different metrics: half-life, clearance)
  - Infectious disease (different endpoints: viral load, infection rate)
- Verify no data loss compared to Phase 1
- Check for hallucinations in extraction

### Phase 4 Testing
- Verify citations are accurate and clickable
- Check confidence scores are correct
- Test contradiction detection
- User acceptance testing (can non-technical users understand confidence labels?)

---

## Success Metrics

### Phase 1
- [ ] All template fields editable in UI
- [ ] Real-time preview updates
- [ ] Users can correct extraction errors without code changes

### Phase 2
- [ ] Extraction works on non-Semaglutide trials
- [ ] No hardcoded trial metadata
- [ ] Flexible schema accommodates 1-N outcomes/arms/safety events
- [ ] Extraction error rate on diverse trials ≤ 15%

### Phase 3
- [ ] Template renders correctly for simple trials (1-2 outcomes)
- [ ] Template renders correctly for complex trials (5+ outcomes)
- [ ] No blank sections in output
- [ ] Professional appearance maintained

### Phase 4
- [ ] 100% of values have citations
- [ ] Confidence scores assigned to all fields
- [ ] Contradictions in data are detected
- [ ] Users trust the system (measured by manual review rate)

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Phase 2 refactor breaks existing functionality | High | Keep Phase 1 (editable UI) working, test on Semaglutide trial throughout |
| LLM extraction hallucinations increase | High | Implement Phase 4 validation chains early, don't wait for Phase 3 |
| Flexible schema becomes unmaintainable | Medium | Define schema clearly in `schemas/trial_schemas.py`, use dataclasses |
| Users misunderstand low-confidence values | Medium | Design UI carefully, test with users, provide clear documentation |
| Complex trials produce cluttered visuals | Medium | Plan adaptive layout carefully, prototype early with real examples |

---

## Future Enhancements (Out of Scope)

- Multi-language support
- Batch processing (multiple papers)
- Export to PDF, SVG, PowerPoint formats
- Collaborative editing (multiple users)
- Version history/audit trail
- Integration with medical databases (PubMed, ClinicalTrials.gov)
- Custom template builder
- Automated quality scoring for abstracts

---

## References

### Related Code
- [app.py](file:///Users/Noralroub/MGT802_final_project/app.py) — Main Streamlit app
- [agents/extraction_agent.py](file:///Users/Noralroub/MGT802_final_project/agents/extraction_agent.py) — Current extraction pipeline
- [utils/data_extraction.py](file:///Users/Noralroub/MGT802_final_project/utils/data_extraction.py) — Current data extraction
- [core/visual_abstract.py](file:///Users/Noralroub/MGT802_final_project/core/visual_abstract.py) — Visual abstract rendering
- [ui/visual_template.py](file:///Users/Noralroub/MGT802_final_project/ui/visual_template.py) — UI components

### External References
- PICOT framework: https://libguides.uwo.ca/c.php?g=651055&p=4567959
- Clinical trial design: https://www.fda.gov/media/132637/download
- Adverse event reporting: MedDRA terminology

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-07 | Claude Code | Initial plan created |

---

## Questions & Decisions to Make

1. **Trial Classification**: Should this be user-selected or auto-detected?
   - *Suggested*: Auto-detect, with user override option

2. **Schema Evolution**: How do we handle new trial types discovered later?
   - *Suggested*: Use extensible dataclasses, add new outcome types as needed

3. **Citation Granularity**: How detailed should source citations be?
   - *Suggested*: Page number + section + exact quote

4. **Confidence Scoring**: Rule-based or learned from validation chains?
   - *Suggested*: Rule-based first (no training data), upgrade to learned later

5. **User Edits**: Should edits override LLM or merge with validation?
   - *Suggested*: Edits override, validation adds confidence warnings

