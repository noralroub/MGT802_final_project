# Sprint 4 Plan: Visual Abstract Generation

## Overview

Sprint 4 transforms the QA system outputs into visual abstracts - professional infographics that summarize key findings from cardiovascular trial papers. These will be displayed in a Streamlit web interface.

**Goal**: Create an interactive web app where users can:
1. Upload a PDF
2. Get automated answers to key trial questions
3. View a visual summary (infographic) of the trial results

---

## Architecture

### Data Flow

```
User Upload PDF
    ↓
[Sprints 1-3] Extract, embed, answer questions
    ↓
[Sprint 4a] Parse answers → Extract structured data
    ↓
[Sprint 4b] Design visual layout
    ↓
[Sprint 4c] Generate infographic (matplotlib/plotly)
    ↓
[Sprint 4d] Streamlit UI → Display and interact
    ↓
User views professional visual abstract
```

### Components Structure

```
sprint_4/
├── core/
│   └── visual_abstract.py      # Main abstract generator class
├── utils/
│   ├── data_extraction.py      # Parse LLM answers → structured data
│   ├── layout_designer.py      # Define visual layouts
│   └── chart_builder.py        # Create visualizations
├── templates/
│   ├── semaglutide_template.json    # Trial-specific layout
│   └── generic_trial_template.json  # Fallback for other trials
├── app_streamlit.py            # Streamlit UI
├── debug_visual_abstract.py    # Test script
└── tests/
    └── test_visual_abstract.py # Unit tests
```

---

## Sprint 4 Detailed Breakdown

### **Phase 4a: Data Extraction & Structuring**

**Goal**: Parse LLM answers into structured data for visualization

**Module**: `utils/data_extraction.py`

**Key Functions**:

```python
class TrialDataExtractor:

    def extract_demographics(answer_str) -> dict:
        # From "17,604 patients" → extract number
        # From "8,803 semaglutide, 8,801 placebo" → split arms
        # Returns: {"total": 17604, "semaglutide": 8803, "placebo": 8801}

    def extract_outcomes(answer_str) -> dict:
        # From "HR 0.80 (95% CI 0.72-0.90)" → extract statistics
        # From "6.5% vs 8.0%" → extract event rates
        # Returns: {"hazard_ratio": 0.80, "ci_lower": 0.72, "ci_upper": 0.90, ...}

    def extract_adverse_events(answer_str) -> dict:
        # From "16.6% discontinuation vs 8.2%" → extract rates
        # From "gastrointestinal 10.0% vs 2.0%" → extract specific AEs
        # Returns: {"discontinuation": {semaglutide: 16.6, placebo: 8.2}, ...}

    def extract_dosing(answer_str) -> dict:
        # From "2.4 mg weekly" → extract dose, frequency
        # From "77% at target dose" → extract compliance
        # Returns: {"dose": "2.4 mg", "frequency": "weekly", "at_target": 77}

    def extract_key_metrics(qa_results) -> dict:
        # Consolidate all answers into structured format
        # Returns: Complete trial summary object
```

**Data Structure Output**:

```python
{
    "trial_info": {
        "title": "Semaglutide and Cardiovascular Outcomes...",
        "drug": "Semaglutide",
        "indication": "Obesity without diabetes",
        "trial_name": "SELECT",
        "duration_months": 39.8
    },
    "population": {
        "total_enrolled": 17604,
        "drug_arm": 8803,
        "placebo_arm": 8801,
        "age_mean": 61.6,
        "male_percent": 27.7
    },
    "primary_outcome": {
        "definition": "Composite of CV death, MI, stroke",
        "drug_events": 569,
        "drug_rate": 6.5,
        "placebo_events": 701,
        "placebo_rate": 8.0,
        "hazard_ratio": 0.80,
        "ci_lower": 0.72,
        "ci_upper": 0.90,
        "p_value": "<0.001"
    },
    "adverse_events": {
        "discontinuation": {
            "drug": 16.6,
            "placebo": 8.2
        },
        "gastrointestinal": {
            "drug": 10.0,
            "placebo": 2.0
        }
    },
    "body_weight": {
        "drug_change": -9.39,
        "placebo_change": -0.88,
        "difference": -8.51
    },
    "sponsor": "Novo Nordisk",
    "publication": "NEJM 2023"
}
```

---

### **Phase 4b: Layout Design**

**Goal**: Define visual layouts for different trial types

**Module**: `utils/layout_designer.py`

**Layout Strategy**:

For cardiovascular trials like Semaglutide, create a 2-column or 3-section layout:

```
┌─────────────────────────────────────────────┐
│  TRIAL TITLE & KEY INFO                     │
│  Semaglutide and CV Outcomes in Obesity     │
│  Duration: 39.8 months | n=17,604           │
├──────────────┬──────────────┬───────────────┤
│ POPULATION   │ PRIMARY      │ ADVERSE       │
│              │ OUTCOME      │ EVENTS        │
│              │              │               │
│ • n=17,604   │ • HR: 0.80   │ • Disc: 16.6%│
│ • Age: 61.6  │   (p<0.001)  │   vs 8.2%    │
│ • BMI: 27+   │ • 6.5% vs    │ • GI: 10.0%  │
│              │   8.0%       │   vs 2.0%    │
├──────────────┴──────────────┴───────────────┤
│ BODY WEIGHT CHANGE                          │
│ Semaglutide: -9.39% | Placebo: -0.88%      │
│ Difference: -8.51 percentage points         │
├─────────────────────────────────────────────┤
│ CONCLUSION: Semaglutide superior to         │
│ placebo in reducing CV events               │
└─────────────────────────────────────────────┘
```

**Available Layouts**:

1. **Horizontal 3-panel** (above) - Good for posters
2. **Vertical stacked** - Good for slides/documents
3. **Infographic style** - Visual hierarchy with icons
4. **Single-page comprehensive** - All metrics at once

---

### **Phase 4c: Basic Charts & Icons**

**Goal**: Create simple visual components (basic bars, pie charts, icons) + display text for metrics that don't chart well

**Module**: `utils/chart_builder.py`

**Chart Types** (simplified):

1. **Event Rate Comparison** (Basic bar chart)
   ```
   Semaglutide: 6.5%  ███
   Placebo:     8.0%  ████
   ```

2. **Body Weight Change** (Basic bar chart)
   ```
   Semaglutide: -9.39%  ████████
   Placebo:     -0.88%  █
   ```

3. **Population Breakdown** (Simple pie chart)
   ```
   Semaglutide: 50%  |  Placebo: 50%
   ```

4. **Simple Icons** (Unicode/text-based for visual markers)
   ```
   👥 Population metrics
   🎯 Outcome metrics
   💊 Treatment details
   ⚠️ Adverse events
   ```

**Text-Based Metrics** (displayed as formatted text, not charts):
- Hazard Ratio: "HR: 0.80 (95% CI 0.72-0.90), p<0.001"
- Patient counts and demographics
- Dosing information
- Adverse event percentages
- Inclusion/exclusion criteria
- Any other metrics not suitable for simple charts

**Technology Stack**:
- **matplotlib**: Basic bar and pie charts only
- **PIL/pillow**: Image composition
- Unicode text characters for icons
- Formatted text strings for metrics

---

### **Phase 4d: Streamlit Integration**

**Goal**: Create interactive web interface

**Module**: `app_streamlit.py`

**Features**:

```python
# Page 1: Upload & Analysis
- File uploader for PDF
- Progress bar for processing
- "Generate Abstract" button
- Results display

# Page 2: Visual Abstract
- Large infographic display
- Key metrics highlighted
- Exportable as PNG/PDF

# Page 3: Detailed Results
- Full QA answers
- Source citations
- Download JSON data

# Sidebar: Configuration
- Choose layout style
- Font size adjustment
- Color scheme selection
- LLM model selector
```

**Streamlit Layout**:

```
┌─────────────────────────────────────────────────┐
│  Medical Visual Abstract Generator               │
├─────────────────────────────────────────────────┤
│                                                  │
│  📄 Upload PDF                                  │
│  [Choose file...] [Generate Abstract]           │
│                                                  │
│  ─────────────────────────────────────────────  │
│                                                  │
│  Visual Abstract Preview:                       │
│  [Infographic Image]                            │
│                                                  │
│  [Download PNG] [Download PDF] [View Details]   │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Implementation Plan

### **Step 1: Data Extraction** (20 min)

Create `utils/data_extraction.py`:
- Parse QA answers using regex/NLP
- Extract numbers, statistics, percentages
- Build structured trial data object
- Handle missing/malformed data gracefully

**Test with**: QA results from Sprint 3 (already have 7 answers)

---

### **Step 2: Layout Design** (15 min)

Create `utils/layout_designer.py`:
- Define layout templates as config
- Support multiple layout styles
- Handle dynamic content sizing
- Style definitions (fonts, colors, spacing)

**Layouts to implement**:
1. Horizontal 3-panel (recommended for Semaglutide trial)
2. Vertical stacked (backup)

---

### **Step 3: Basic Charts & Icons** (15 min)

Create `utils/chart_builder.py`:
- Simple event rate bar chart (side-by-side bars)
- Simple body weight change bar chart
- Simple population pie chart (drug vs placebo)
- Unicode emoji icons for section markers
- Format text for metrics that don't chart well (hazard ratios, confidence intervals, p-values, etc.)
- All charts use matplotlib with minimal styling

**Use**: matplotlib for basic bars/pie charts only; formatted text for complex metrics

---

### **Step 4: Visual Abstract Generator** (20 min)

Create `core/visual_abstract.py`:
- `VisualAbstractGenerator` class
- `generate_abstract()` - orchestrate all steps
- `export_as_image()` - save to PNG
- `export_as_pdf()` - optional future feature

```python
class VisualAbstractGenerator:
    def __init__(self, qa_results):
        self.trial_data = TrialDataExtractor.extract(qa_results)

    def generate_abstract(self, layout="horizontal_3panel"):
        # Step 1: Prepare data
        # Step 2: Choose layout
        # Step 3: Build charts
        # Step 4: Compose image
        return abstract_image

    def export_as_image(self, filename):
        # Save to PNG
        pass
```

---

### **Step 5: Streamlit App** (20 min)

Create `app_streamlit.py`:
- PDF uploader
- Processing pipeline (ingest → answer → abstract)
- Display abstract with metrics
- Export options

```python
import streamlit as st
from core.qa import QASystem
from core.visual_abstract import VisualAbstractGenerator

st.title("Medical Visual Abstract Generator")

# Upload
pdf_file = st.file_uploader("Upload PDF", type="pdf")

if pdf_file:
    # Process
    qa = QASystem(pdf_path=pdf_file)
    answers = qa.batch_query([...key questions...])

    # Generate abstract
    generator = VisualAbstractGenerator(answers)
    abstract = generator.generate_abstract()

    # Display
    st.image(abstract)
    st.download_button("Download PNG", ...)
```

---

### **Step 6: Debug Script** (15 min)

Create `debug_visual_abstract.py`:
- Test with QA results from Sprint 3
- Show generated abstract
- Save to file for inspection

---

### **Step 7: Unit Tests** (15 min)

Create `tests/test_visual_abstract.py`:
- Test data extraction accuracy
- Test chart generation
- Test layout composition
- Test image export

---

### **Step 8: Documentation** (10 min)

Create `SPRINT_4_README.md`:
- Architecture overview
- Component documentation
- Usage examples
- Customization guide

---

## Technical Decisions

### **1. Visualization Library**

| Option | Pros | Cons |
|--------|------|------|
| **matplotlib** | Publication quality, static | Less interactive |
| **plotly** | Interactive, modern | More overhead |
| **PIL only** | Simple, lightweight | Limited chart types |
| **matplotlib + plotly** | Best of both | More complex |

**Recommendation**: Start with **matplotlib** for static, high-quality abstract. Can add Plotly charts for interactive dashboard later.

---

### **2. Data Extraction Approach**

| Option | Pros | Cons |
|--------|------|------|
| **Regex parsing** | Simple, fast | Fragile with format changes |
| **NLP entity extraction** | Robust | More complex |
| **Structured LLM output** | Perfect accuracy | Requires LLM change |
| **Hybrid (regex + NLP)** | Balanced | Most complex |

**Recommendation**: Start with **regex** for common patterns. Fall back to "value not extracted" if needed. This is 80/20 solution.

---

### **3. Layout Configuration**

| Option | Pros | Cons |
|--------|------|------|
| **Hardcoded positions** | Simple | Inflexible |
| **JSON config files** | Flexible | More code |
| **Template classes** | Scalable | More abstraction |

**Recommendation**: **JSON config files** - allows easy customization without code changes.

---

### **4. Color & Styling**

**Default color scheme** (medical/professional):
- Primary: Blue (#1f77b4)
- Highlight: Red (#d62728) for key metrics
- Background: White (#ffffff)
- Text: Dark gray (#262730)
- Grid: Light gray (#f0f2f6)

**Alternative schemes available**:
- Dark mode
- Colorblind-friendly
- Journal-specific (NEJM, Circulation, etc.)

---

## Expected Output Examples

### **Example 1: Semaglutide Trial Abstract**

```
┌────────────────────────────────────────────────────┐
│  SEMAGLUTIDE AND CARDIOVASCULAR OUTCOMES           │
│  IN OBESITY WITHOUT DIABETES                       │
│  The SELECT Trial | NEJM 2023                      │
├────────────────────────────────────────────────────┤
│                                                     │
│  👥 POPULATION              🎯 PRIMARY OUTCOME     │
│  • n = 17,604               • HR: 0.80             │
│  • Age: 61.6 years          • 95% CI: 0.72-0.90   │
│  • Female: 27.7%            • p < 0.001            │
│  • Semaglutide: 8,803        • Event rate:         │
│  • Placebo: 8,801              6.5% vs 8.0%       │
│                                                     │
│                    [BAR CHART]                     │
│                 Event Rate: 6.5% vs 8.0%           │
│
├────────────────────────────────────────────────────┤
│  💊 TREATMENT                ⚠️ ADVERSE EVENTS     │
│  • Dose: 2.4 mg/week        • Discontinuation:     │
│  • At target: 77%             16.6% vs 8.2%        │
│  • Duration: 39.8 months    • GI Symptoms:         │
│                               10.0% vs 2.0%        │
├────────────────────────────────────────────────────┤
│  BODY WEIGHT CHANGE                                │
│  Semaglutide: -9.39%  |  Placebo: -0.88%           │
│            [BAR CHART]                             │
│  Difference: -8.51 percentage points                │
├────────────────────────────────────────────────────┤
│  ✓ Semaglutide superior to placebo for CV outcomes │
│  ✓ Significant weight reduction achieved           │
│  ⚠ GI side effects more common with drug           │
└────────────────────────────────────────────────────┘
```

---

## Success Criteria

✅ **Sprint 4 is complete when**:

1. **Data Extraction**
   - [ ] Extracts >90% of key metrics from QA answers
   - [ ] Handles missing/malformed data gracefully
   - [ ] Returns structured trial data object

2. **Visualization**
   - [ ] Generates publication-quality infographic
   - [ ] All major findings visible at glance
   - [ ] Professional appearance suitable for presentations

3. **Streamlit App**
   - [ ] Upload PDF → View abstract in <30 seconds
   - [ ] Download PNG/PDF options working
   - [ ] Mobile-responsive layout

4. **Testing**
   - [ ] Unit tests pass for all components
   - [ ] Integration test: Full pipeline works
   - [ ] Manual review: Abstract looks professional

5. **Documentation**
   - [ ] Sprint 4 README complete
   - [ ] Architecture documented
   - [ ] Customization guide provided

---

## Timeline Estimate

| Phase | Task | Time |
|-------|------|------|
| 4a | Data Extraction | 20 min |
| 4b | Layout Design | 15 min |
| 4c | Basic Charts & Icons | 15 min |
| 4d | Streamlit UI | 20 min |
| 4e | Debug Script | 15 min |
| 4f | Unit Tests | 15 min |
| 4g | Documentation | 10 min |
| **Total** | | **110 min (~2 hours)** |

---

## Future Enhancements (Post-Sprint 4)

- [ ] Support multiple trial types (oncology, rheumatology, etc.)
- [ ] PDF export with higher resolution
- [ ] Interactive dashboard with drill-down details
- [ ] Batch processing (multiple PDFs)
- [ ] API endpoint for external integrations
- [ ] Multi-language support
- [ ] Real-time collaboration features

---

## Questions for Review

Before we proceed, please review and let me know:

1. **Data Extraction**:
   - Should we use regex parsing or something more sophisticated?
   - Are there other metrics you want extracted beyond what's listed?

2. **Layout**:
   - Do you prefer the 3-panel horizontal layout?
   - Should we support multiple layouts from the start?

3. **Visualization**:
   - What chart types are most important for your use case?
   - Any specific styling preferences (colors, fonts)?

4. **Streamlit App**:
   - Should processing happen in real-time or with a button click?
   - Do you want to save PDFs, or just PNGs?

5. **Scope**:
   - Should we focus only on semaglutide/cardiovascular trials initially?
   - Or build it generic for any trial type?

---

**Ready to implement once you review and approve!**
