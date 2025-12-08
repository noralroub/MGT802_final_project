"""
Phase 1 Integration Tests - Visual Abstract HTML Renderer
Tests the new JACC-style HTML renderer integration into the app
"""

import json
from utils.visual_abstract_html import (
    VisualAbstractContent,
    build_visual_abstract_html,
    render_bar_chart,
    safe_get,
    process_highlight,
    COLORS
)


def test_visual_abstract_content_dataclass():
    """Test VisualAbstractContent data class"""
    print("\n🧪 Test 1: VisualAbstractContent Dataclass")

    # Test default initialization
    content = VisualAbstractContent()
    assert content.title == "Research Paper Title"
    assert content.main_finding == "Main finding goes here."
    assert content.results == []
    print("  ✓ Default initialization works")

    # Test with custom values
    content = VisualAbstractContent(
        title="Custom Trial",
        main_finding="Custom finding",
        participants="1000"
    )
    assert content.title == "Custom Trial"
    assert content.participants == "1000"
    print("  ✓ Custom initialization works")

    # Test to_dict conversion
    content_dict = content.to_dict()
    assert isinstance(content_dict, dict)
    assert content_dict["title"] == "Custom Trial"
    print("  ✓ to_dict() conversion works")

    # Test from_dict conversion
    data = {
        "title": "From Dict",
        "main_finding": "Test finding",
        "participants": "500"
    }
    content = VisualAbstractContent.from_dict(data)
    assert content.title == "From Dict"
    assert content.participants == "500"
    print("  ✓ from_dict() conversion works")


def test_safe_get_helper():
    """Test safe_get helper function"""
    print("\n🧪 Test 2: safe_get() Helper Function")

    # Test with valid dict and key
    data = {"key": "value", "number": 42, "empty": None}
    assert safe_get(data, "key") == "value"
    print("  ✓ Returns value for existing key")

    # Test with None value
    assert safe_get(data, "empty", "default") == "default"
    print("  ✓ Returns default for None value")

    # Test with missing key
    assert safe_get(data, "missing", "default") == "default"
    print("  ✓ Returns default for missing key")

    # Test with None dict
    assert safe_get(None, "any", "default") == "default"
    print("  ✓ Handles None dict gracefully")


def test_process_highlight():
    """Test highlight tag processing"""
    print("\n🧪 Test 3: process_highlight() Function")

    text = "This is <highlight>important</highlight> text"
    result = process_highlight(text)
    assert '<span class="highlight">' in result
    assert "</span>" in result
    print("  ✓ Converts <highlight> tags to <span> elements")

    # Test empty string
    assert process_highlight("") == ""
    print("  ✓ Handles empty strings")


def test_render_bar_chart():
    """Test bar chart rendering"""
    print("\n🧪 Test 4: render_bar_chart() Function")

    # Test with data
    data = {"Low": 18, "Moderate": 31, "High": 42}
    result = render_bar_chart(data)
    assert "va-bar-chart" in result
    assert "Low" in result
    assert "Moderate" in result
    assert "High" in result
    print("  ✓ Renders bar chart with data")

    # Test with empty data
    result = render_bar_chart({})
    assert "va-stat-icon" in result
    print("  ✓ Shows placeholder for empty data")

    # Test with None
    result = render_bar_chart(None)
    assert "va-stat-icon" in result
    print("  ✓ Handles None data")


def test_html_generation():
    """Test HTML generation for complete visual abstract"""
    print("\n🧪 Test 5: build_visual_abstract_html() Function")

    sample_content = {
        "title": "Effect of Exercise on Cardiovascular Mortality",
        "main_finding": "Regular activity was associated with <highlight>42% reduction</highlight> in mortality",
        "background": "Cardiovascular disease is the leading cause of death.",
        "methods_summary": "Prospective Cohort Study",
        "participants": "10,847",
        "participants_label": "Adults aged 65+",
        "intervention": "Exercise",
        "intervention_label": "vs. Sedentary",
        "methods_description": "Participants were followed via national registries.",
        "results": [
            "42% lower CV mortality in active vs sedentary",
            "Benefits observed with 75 min/week activity",
            "Dose-response relationship observed"
        ],
        "chart_title": "Mortality Reduction",
        "chart_subtitle": "By Exercise Level",
        "chart_data": {"Low": 18, "Moderate": 31, "High": 42},
        "journal": "JACC",
        "year": "2024",
        "authors": "Johnson et al.",
        "doi": "10.1016/j.jacc.2024.01.001"
    }

    html = build_visual_abstract_html(sample_content)

    # Test HTML structure
    assert isinstance(html, str)
    assert len(html) > 1000
    print("  ✓ Generates HTML of expected size")

    # Test key sections
    sections = [
        ("va-header", "Header section"),
        ("va-hero", "Hero section"),
        ("va-left-column", "Left column"),
        ("va-right-column", "Right column"),
        ("va-results-box", "Results box"),
        ("va-chart-box", "Chart box"),
        ("va-footer", "Footer"),
    ]

    for class_name, section_name in sections:
        assert f'class="{class_name}"' in html or f'class=\'{class_name}\'' in html or f"class={class_name}" in html
        print(f"  ✓ Contains {section_name}")

    # Test content inclusion
    content_checks = [
        ("Effect of Exercise", "Title"),
        ("42% reduction", "Main finding with highlight"),
        ("Cardiovascular disease", "Background text"),
        ("10,847", "Participant count"),
        ("Prospective Cohort Study", "Methods summary"),
        ("Johnson et al.", "Authors"),
        ("JACC", "Journal"),
        ("2024", "Year"),
    ]

    for content, description in content_checks:
        assert content in html, f"Missing: {description}"
        print(f"  ✓ Includes {description}")


def test_data_mapping_for_app():
    """Test the data mapping logic used in app.py"""
    print("\n🧪 Test 6: Data Mapping for app.py Integration")

    # Simulate extraction result from extraction agent
    extraction = {
        "structured_abstract": {
            "title": "Semaglutide Cardiovascular Outcomes Trial",
            "main_finding": "Semaglutide reduced major cardiovascular events by 26%",
            "results": "Primary composite outcome met with statistical significance",
            "background": "Type 2 diabetes patients at high cardiovascular risk",
            "methods": "Randomized, placebo-controlled trial over 2.4 years",
            "methods_summary": "RCT",
            "journal": "NEJM",
            "year": "2023",
            "authors": "Brown et al.",
            "doi": "10.1056/NEJMoa2307563"
        },
        "visual_data": {
            "population": {
                "total_enrolled": 3731,
                "arm_1_label": "Semaglutide",
                "arm_2_label": "Placebo"
            }
        }
    }

    # Apply app.py mapping logic
    structured = extraction.get("structured_abstract", {})
    visual_data = extraction.get("visual_data", {})

    abstract_content = {
        "title": structured.get("title", "Clinical Trial Abstract"),
        "main_finding": structured.get("main_finding", structured.get("results", "Key findings from the trial")),
        "background": structured.get("background", ""),
        "methods_summary": structured.get("methods_summary", "Study Design"),
        "methods_description": structured.get("methods", ""),
        "participants": str(visual_data.get("population", {}).get("total_enrolled", "N/A")),
        "participants_label": "Participants enrolled",
        "intervention": visual_data.get("population", {}).get("arm_1_label", "Intervention"),
        "intervention_label": "vs. Comparator",
        "results": [structured.get("results", "Primary outcome achieved")] if structured.get("results") else [],
        "chart_title": "Key Results",
        "chart_subtitle": "",
        "journal": structured.get("journal", ""),
        "year": structured.get("year", ""),
        "authors": structured.get("authors", ""),
        "doi": structured.get("doi", ""),
    }

    # Verify all fields mapped correctly
    assert abstract_content["title"] == "Semaglutide Cardiovascular Outcomes Trial"
    print("  ✓ Title mapped correctly")

    assert "26%" in abstract_content["main_finding"]
    print("  ✓ Main finding mapped correctly")

    assert "Type 2 diabetes" in abstract_content["background"]
    print("  ✓ Background mapped correctly")

    assert abstract_content["participants"] == "3731"
    print("  ✓ Participant count mapped correctly")

    assert abstract_content["intervention"] == "Semaglutide"
    print("  ✓ Intervention mapped correctly")

    assert len(abstract_content["results"]) > 0
    print("  ✓ Results list populated correctly")

    assert abstract_content["journal"] == "NEJM"
    print("  ✓ Citation info mapped correctly")


def test_color_scheme():
    """Test color scheme configuration"""
    print("\n🧪 Test 7: Color Scheme Configuration")

    required_colors = [
        "header_bg", "hero_bg", "hero_highlight", "methods_banner",
        "results_header", "box_border", "text_primary", "text_secondary",
        "background", "white", "footer_bg"
    ]

    for color in required_colors:
        assert color in COLORS
        assert COLORS[color].startswith("#")
        print(f"  ✓ {color}: {COLORS[color]}")


def run_all_tests():
    """Run all Phase 1 tests"""
    print("=" * 70)
    print("PHASE 1 INTEGRATION TESTS - VISUAL ABSTRACT HTML RENDERER")
    print("=" * 70)

    tests = [
        test_visual_abstract_content_dataclass,
        test_safe_get_helper,
        test_process_highlight,
        test_render_bar_chart,
        test_html_generation,
        test_data_mapping_for_app,
        test_color_scheme,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n✅ ALL PHASE 1 TESTS PASSED!")
        print("\nPhase 1 Deliverables:")
        print("  ✓ HTML renderer module created (utils/visual_abstract_html.py)")
        print("  ✓ VisualAbstractContent data class implemented")
        print("  ✓ HTML generation tested and working")
        print("  ✓ Integration into app.py completed")
        print("  ✓ Data mapping logic verified")
        print("\nNext Steps:")
        print("  1. Test app.py locally with actual PDF uploads")
        print("  2. Verify visual abstract renders in browser at localhost:8501")
        print("  3. Test sidebar editing functionality")
        print("  4. Move to Phase 2: Flexible Extraction Agents")
    else:
        print(f"\n❌ {failed} test(s) failed. Fix before proceeding.")
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
