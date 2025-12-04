"""Test script for Sprint 4 Steps 1-3 modules."""

import json
from utils.data_extraction import TrialDataExtractor
from utils.layout_designer import LayoutDesigner
from utils.chart_builder import ChartBuilder


def test_data_extraction():
    """Test data extraction module."""
    print("\n" + "=" * 70)
    print("TEST 1: DATA EXTRACTION MODULE")
    print("=" * 70)

    extractor = TrialDataExtractor()
    qa_results = extractor.load_qa_results('data/debug_output/qa_results.json')
    trial_data = extractor.extract_key_metrics(qa_results)

    print("\n✓ Loaded QA results from Sprint 3")
    print(f"  - Model: {qa_results['model']}")
    print(f"  - Questions answered: {qa_results['num_questions']}")

    print("\n✓ Extracted trial data:")
    print(f"  Trial: {trial_data['trial_info']['title']}")
    print(f"  Publication: {trial_data['trial_info']['publication']}")

    print("\n✓ Population metrics:")
    pop = trial_data['population']
    print(f"  - Total: {pop['total_enrolled']:,}")
    print(f"  - Drug arm: {pop['drug_arm']:,}")
    print(f"  - Placebo arm: {pop['placebo_arm']:,}")

    print("\n✓ Primary outcome:")
    outcome = trial_data['primary_outcome']
    print(f"  - HR: {outcome['hazard_ratio']}")
    print(f"  - 95% CI: {outcome['ci_lower']}-{outcome['ci_upper']}")
    print(f"  - P-value: {outcome['p_value']}")
    print(f"  - Event rates: {outcome['semaglutide_rate']}% vs {outcome['placebo_rate']}%")

    print("\n✓ Body weight changes:")
    bw = trial_data['body_weight']
    print(f"  - Semaglutide: {bw['semaglutide_change']}%")
    print(f"  - Placebo: {bw['placebo_change']}%")
    print(f"  - Difference: {bw['difference']} percentage points")

    print("\n✓ Adverse events:")
    ae = trial_data['adverse_events']
    print(f"  - Discontinuation: {ae['discontinuation']['drug']}% vs {ae['discontinuation']['placebo']}%")
    print(f"  - GI symptoms: {ae['gastrointestinal']['drug']}% vs {ae['gastrointestinal']['placebo']}%")

    print("\n✓ Dosing:")
    dose = trial_data['dosing']
    print(f"  - Dose: {dose['dose']} {dose['frequency']}")
    print(f"  - At target: {dose['at_target_percent']}%")

    print("\n✅ DATA EXTRACTION TEST PASSED\n")
    return trial_data


def test_layout_design(trial_data):
    """Test layout designer module."""
    print("=" * 70)
    print("TEST 2: LAYOUT DESIGN MODULE")
    print("=" * 70)

    designer = LayoutDesigner("horizontal_3panel")

    print("\n✓ Layout created: horizontal_3panel")
    width, height = designer.get_image_dimensions()
    print(f"  - Canvas size: {width}x{height}px")

    print("\n✓ Defined sections:")
    sections = designer.get_all_sections()
    for section_name in ["header", "population", "outcome", "adverse", "treatment", "body_weight", "conclusion"]:
        section = sections[section_name]
        print(f"  - {section_name:15} @ ({section['x']:4}, {section['y']:4}) "
              f"| {section['width']:4}x{section['height']:3}px", end="")
        if 'icon' in section:
            print(f" | Icon: {section['icon']}", end="")
        print()

    print("\n✓ Color scheme:")
    colors = designer.get_colors()
    print(f"  - Population BG:  RGB{colors.population_bg}")
    print(f"  - Outcome BG:     RGB{colors.outcome_bg}")
    print(f"  - Adverse BG:     RGB{colors.adverse_bg}")
    print(f"  - Drug color:     RGB{colors.drug_bar}")
    print(f"  - Placebo color:  RGB{colors.placebo_bar}")

    print("\n✓ Typography:")
    typo = designer.get_typography()
    print(f"  - Title size:          {typo.title_size}pt")
    print(f"  - Section header size: {typo.section_header_size}pt")
    print(f"  - Label size:          {typo.label_size}pt")
    print(f"  - Value size:          {typo.value_size}pt")

    print("\n✅ LAYOUT DESIGN TEST PASSED\n")
    return designer


def test_chart_builder(trial_data):
    """Test chart builder module."""
    print("=" * 70)
    print("TEST 3: CHART BUILDER MODULE")
    print("=" * 70)

    builder = ChartBuilder()
    pop = trial_data['population']
    outcome = trial_data['primary_outcome']
    bw = trial_data['body_weight']

    print("\n✓ Creating event rate chart...")
    event_chart = builder.create_event_rate_chart(
        outcome['semaglutide_rate'],
        outcome['placebo_rate']
    )
    event_bytes = event_chart.getbuffer().nbytes
    print(f"  - Size: {event_bytes:,} bytes")
    event_chart.seek(0)

    print("\n✓ Creating body weight chart...")
    weight_chart = builder.create_body_weight_chart(
        bw['semaglutide_change'],
        bw['placebo_change']
    )
    weight_bytes = weight_chart.getbuffer().nbytes
    print(f"  - Size: {weight_bytes:,} bytes")
    weight_chart.seek(0)

    print("\n✓ Creating population pie chart...")
    pie_chart = builder.create_population_pie_chart(
        pop['drug_arm'],
        pop['placebo_arm']
    )
    pie_bytes = pie_chart.getbuffer().nbytes
    print(f"  - Size: {pie_bytes:,} bytes")
    pie_chart.seek(0)

    print("\n✓ Generating formatted text:")
    print("\n  Hazard Ratio:")
    hr_text = builder.format_hazard_ratio_text(
        outcome['hazard_ratio'],
        outcome['ci_lower'],
        outcome['ci_upper'],
        outcome['p_value']
    )
    for line in hr_text.split('\n'):
        print(f"    {line}")

    print("\n  Demographics Table:")
    demo_text = builder.create_demographics_table(
        pop['total_enrolled'],
        pop['drug_arm'],
        pop['placebo_arm'],
        pop['age_mean'],
        pop['bmi_minimum']
    )
    for line in demo_text.split('\n'):
        print(f"    {line}")

    print("\n  Adverse Events Table:")
    ae_text = builder.create_adverse_events_table()
    for line in ae_text.split('\n'):
        print(f"    {line}")

    print("\n✅ CHART BUILDER TEST PASSED\n")


def test_integration():
    """Run all tests in sequence."""
    print("\n" + "=" * 70)
    print("SPRINT 4 INTEGRATION TEST - Steps 1-3")
    print("=" * 70)

    # Test all modules
    trial_data = test_data_extraction()
    layout = test_layout_design(trial_data)
    test_chart_builder(trial_data)

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("\n✅ All 3 modules working correctly:")
    print("  1. Data Extraction    - ✓ Parses QA answers to structured data")
    print("  2. Layout Designer    - ✓ Defines infographic layout")
    print("  3. Chart Builder      - ✓ Creates charts and formatted text")
    print("\n✅ Next steps:")
    print("  4. Visual Abstract Generator - Compose all components")
    print("  5. Streamlit App - Display in web interface")
    print("  6. Debug Script - Test full pipeline")
    print("  7. Unit Tests - Verify all components")
    print("  8. Documentation - Write README")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    test_integration()
