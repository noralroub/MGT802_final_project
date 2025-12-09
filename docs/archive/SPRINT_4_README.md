# Sprint 4: Visual Abstract Generation

## Overview

Sprint 4 completes the Medical Visual Abstract Generator system by composing extracted trial data and generated charts into professional infographics. The system transforms clinical trial PDFs into visual summaries suitable for presentations, reports, and publications.

**Architecture:**
```
PDF Upload → Extract & Chunk → Embed → Retrieve → Answer Questions
    ↓
QA Results → Extract Metrics → Design Layout → Compose Infographic
    ↓
Visual Abstract (PNG) → Display in Streamlit → Download & Share
```

## Components

### 1. Data Extraction (`utils/data_extraction.py`)

Parses QA answers into structured trial data.

**Key Classes:**
- `TrialDataExtractor`: Extracts metrics from QA answers using regex patterns

**Key Methods:**
- `extract_demographics()`: Population and demographics
- `extract_outcomes()`: Primary outcomes with statistics
- `extract_adverse_events()`: Safety data
- `extract_dosing()`: Treatment information
- `extract_body_weight()`: Body weight changes
- `extract_key_metrics()`: Consolidated extraction

**Example:**
```python
from utils.data_extraction import TrialDataExtractor

extractor = TrialDataExtractor()
qa_results = extractor.load_qa_results('data/debug_output/qa_results.json')
trial_data = extractor.extract_key_metrics(qa_results)

print(f"Total patients: {trial_data['population']['total_enrolled']}")
print(f"Hazard ratio: {trial_data['primary_outcome']['hazard_ratio']}")
```

### 2. Layout Designer (`utils/layout_designer.py`)

Defines infographic layout and visual design.

**Key Classes:**
- `LayoutDesigner`: Manages layout, colors, and typography
- `Dimensions`: Image dimensions and spacing
- `Colors`: Color scheme for sections
- `Typography`: Font settings

**Supported Layouts:**
- `horizontal_3panel`: 3-column layout (recommended) - 1400x1800px
- `vertical_stacked`: Vertical stacking alternative

**Example:**
```python
from utils.layout_designer import LayoutDesigner

designer = LayoutDesigner("horizontal_3panel")
width, height = designer.get_image_dimensions()  # (1400, 1800)

section = designer.get_section("population")
colors = designer.get_colors()
typography = designer.get_typography()
```

### 3. Chart Builder (`utils/chart_builder.py`)

Creates simple matplotlib charts and formatted text.

**Key Classes:**
- `ChartBuilder`: Generates charts and formatted text

**Chart Types:**
- `create_event_rate_chart()`: Side-by-side bar chart
- `create_body_weight_chart()`: Weight change comparison
- `create_population_pie_chart()`: Population breakdown
- `create_demographics_table()`: Formatted demographics
- `create_adverse_events_table()`: Formatted AE summary
- `format_hazard_ratio_text()`: HR with CI and p-value

**Example:**
```python
from utils.chart_builder import ChartBuilder

builder = ChartBuilder()

# Create charts
event_chart = builder.create_event_rate_chart(6.5, 8.0)
weight_chart = builder.create_body_weight_chart(-9.39, -0.88)
pie_chart = builder.create_population_pie_chart(8803, 8801)

# Format text
hr_text = builder.format_hazard_ratio_text(0.80, 0.72, 0.90, "<0.001")
```

### 4. Visual Abstract Generator (`core/visual_abstract.py`)

Composes all components into final infographic.

**Key Classes:**
- `VisualAbstractGenerator`: Orchestrates infographic generation

**Key Methods:**
- `load_trial_data()`: Load from QA results
- `generate_abstract()`: Create infographic
- `export_as_png()`: Save to PNG file
- `export_as_bytes()`: Return as bytes

**Example:**
```python
from core.visual_abstract import VisualAbstractGenerator

# Initialize with QA results
generator = VisualAbstractGenerator("data/debug_output/qa_results.json")

# Generate infographic
image = generator.generate_abstract()

# Export
generator.export_as_png("output/trial_abstract.png")
png_bytes = generator.export_as_bytes()
```

### 5. Streamlit App (`app_streamlit.py`)

Web interface for the system.

**Features:**
- **Tab 1: Upload & Process**: Upload PDF, run QA pipeline
- **Tab 2: Visual Abstract**: Display infographic, download PNG
- **Tab 3: Detailed Results**: View QA answers, download JSON

**Run:**
```bash
streamlit run app_streamlit.py
```

**Usage:**
1. Upload a clinical trial PDF (or use test file)
2. Click "Generate Visual Abstract"
3. View infographic in Tab 2
4. Download as PNG
5. View detailed Q&A in Tab 3

### 6. Debug Script (`debug_visual_abstract.py`)

Test pipeline end-to-end with existing QA results.

**Run:**
```bash
python3 debug_visual_abstract.py
```

**Output:**
- Verifies all extraction steps
- Generates infographic
- Exports as PNG
- Reports file size and metrics

## Testing

### Unit Tests (`tests/test_visual_abstract.py`)

Comprehensive test coverage:

```bash
pytest tests/test_visual_abstract.py -v
```

**Test Coverage:**
- Data extraction: 7 tests
- Layout design: 6 tests
- Chart builder: 7 tests
- Visual abstract generator: 6 tests
- Integration tests: 2 tests

**Results:** 28/28 tests passing ✅

### Integration Tests

Full pipeline test:
```bash
python3 test_sprint4_progress.py
```

Verifies:
1. Data extraction works
2. Layout design works
3. Chart builder works
4. All components integrate

## Output Format

### Generated Infographic

**File:** `data/debug_output/trial_abstract.png`

**Size:** 1400x1800 pixels, ~70KB

**Layout Sections:**
```
┌─────────────────────────────────────────┐
│         HEADER (Trial Title)            │
├────────┬────────────┬──────────────────┤
│ 👥 POP │ 🎯 OUTCOME │ ⚠️ ADVERSE EVENTS│
├────────┴────────────┴──────────────────┤
│          💊 TREATMENT INFO             │
├─────────────────────────────────────────┤
│          BODY WEIGHT CHANGE             │
├─────────────────────────────────────────┤
│          KEY CONCLUSIONS                │
├─────────────────────────────────────────┤
│            FOOTER                       │
└─────────────────────────────────────────┘
```

### Section Contents

**Population:**
- Total enrolled
- Drug/Placebo split
- Mean age
- BMI requirement

**Primary Outcome:**
- Hazard ratio
- 95% CI
- P-value
- Event rates (%)

**Adverse Events:**
- Discontinuation rates
- GI symptoms
- Serious adverse events

**Treatment:**
- Dose and frequency
- Percentage at target dose

**Body Weight:**
- Semaglutide change (%)
- Placebo change (%)
- Difference (percentage points)

## Configuration

### Color Scheme

- Population: Light blue RGB(230, 240, 255)
- Outcome: Light green RGB(230, 255, 240)
- Adverse: Light orange RGB(255, 245, 230)
- Treatment: Light purple RGB(245, 230, 255)
- Drug data: Blue RGB(31, 119, 180)
- Placebo data: Orange RGB(255, 127, 14)

### Typography

- Title: 28pt
- Section headers: 16pt
- Labels: 13pt
- Values: 14pt
- Small text: 11pt

### Image Dimensions

- Canvas: 1400 x 1800 pixels
- Margin: 40px
- Padding: 20px per section
- Column width: 426px (3 columns)

## Dependencies

```
matplotlib==3.8.2  # Chart generation
Pillow==10.1.0     # Image composition
streamlit==1.28.1  # Web interface
openai==1.51.0     # LLM API
chromadb==0.4.17   # Vector DB
```

## Performance

### Processing Time

- Data extraction: ~1-2 seconds
- Infographic generation: ~2-3 seconds
- PNG export: <1 second
- **Total per PDF: 3-5 seconds**

### File Sizes

- PNG infographic: ~70 KB
- JSON QA results: ~15 KB
- Chroma embeddings: ~50-100 MB per document

## Troubleshooting

### "No trial data loaded"

**Issue:** `ValueError: No trial data loaded. Call load_trial_data() first.`

**Solution:** Initialize with QA results path or call `load_trial_data()`

```python
# Option 1
generator = VisualAbstractGenerator("path/to/qa_results.json")

# Option 2
generator = VisualAbstractGenerator()
generator.load_trial_data("path/to/qa_results.json")
```

### "No image generated"

**Issue:** `ValueError: No image generated. Call generate_abstract() first.`

**Solution:** Call `generate_abstract()` before exporting

```python
image = generator.generate_abstract()
generator.export_as_png("output.png")
```

### Poor text rendering

**Issue:** System fonts not available on your OS

**Solution:** The code falls back to PIL default font. Install system fonts or modify `_get_font()` method to use custom fonts:

```python
def _get_font(self, size: int):
    try:
        return ImageFont.truetype("/path/to/font.ttf", size)
    except:
        return ImageFont.load_default()
```

### Streamlit file upload issues

**Issue:** Large PDFs fail to upload

**Solution:**
- Increase Streamlit memory limit: `streamlit run app.py --logger.level=debug`
- Use smaller PDFs for testing
- Check file size limit in config

## Future Enhancements

- [ ] Support multiple layout templates
- [ ] Custom color schemes
- [ ] Interactive chart generation
- [ ] PDF export with multiple pages
- [ ] Batch processing (multiple PDFs)
- [ ] API endpoint for integration
- [ ] Caching for faster re-generation
- [ ] Multi-language support

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## Contributing

To add new chart types or layouts:

1. Add chart method to `ChartBuilder`
2. Define section in `LayoutDesigner`
3. Add drawing method to `VisualAbstractGenerator`
4. Add tests to `tests/test_visual_abstract.py`
5. Update this README

## License

This project is part of MGT802 Final Project
