"""
Test Study Classifier Agent

Tests the study classifier's ability to:
- Parse classifier output JSON
- Validate classification metadata
- Handle various study types
"""

from agents.study_classifier import StudyClassifier
import json


def test_json_parsing():
    """Test that classifier can parse JSON from text with surrounding text."""
    print("=" * 70)
    print("Test 1: JSON Parsing from Messy Response")
    print("=" * 70)

    classifier = StudyClassifier()

    # Simulate messy LLM output
    messy_response = """
    Let me analyze this study...

    {
        "study_type": "randomized_controlled_trial",
        "design": "parallel",
        "num_arms": 2,
        "arm_labels": ["Semaglutide", "Placebo"],
        "num_primary_outcomes": 1,
        "primary_outcome_names": ["Serious cardiovascular events"],
        "num_secondary_outcomes": 0,
        "secondary_outcome_names": [],
        "has_safety_analysis": true,
        "has_pharmacokinetic_data": false,
        "follow_up_duration": "40 months",
        "special_design_features": "Multicenter, double-blind, parallel assignment",
        "confidence": "high",
        "notes": "SELECT trial, well-designed RCT"
    }

    This classification shows a standard RCT...
    """

    try:
        parsed = classifier._safe_json_parse(messy_response)
        print("✓ Successfully parsed JSON from messy response")
        print(f"  Study type: {parsed['study_type']}")
        print(f"  Arms: {parsed['num_arms']} ({', '.join(parsed['arm_labels'])})")
        print(f"  Primary outcomes: {parsed['num_primary_outcomes']}")
        print(f"  Confidence: {parsed['confidence']}\n")
    except Exception as e:
        print(f"✗ Failed to parse: {e}\n")
        return False

    return True


def test_classification_validation():
    """Test validation of classification metadata."""
    print("=" * 70)
    print("Test 2: Classification Validation")
    print("=" * 70)

    classifier = StudyClassifier()

    # Valid classification
    valid_classification = {
        "study_type": "randomized_controlled_trial",
        "design": "parallel",
        "num_arms": 2,
        "arm_labels": ["Drug A", "Placebo"],
        "num_primary_outcomes": 1,
        "primary_outcome_names": ["Primary outcome"],
        "num_secondary_outcomes": 2,
        "secondary_outcome_names": ["Secondary 1", "Secondary 2"],
        "has_safety_analysis": True,
        "has_pharmacokinetic_data": False,
        "follow_up_duration": "12 weeks",
        "special_design_features": "",
        "confidence": "high",
        "notes": "",
    }

    if classifier.validate_classification(valid_classification):
        print("✓ Valid classification passed validation\n")
    else:
        print("✗ Valid classification failed validation\n")
        return False

    # Invalid classification (mismatched arm count)
    invalid_classification_1 = valid_classification.copy()
    invalid_classification_1["num_arms"] = 3  # Says 3 but only 2 labels
    if not classifier.validate_classification(invalid_classification_1):
        print("✓ Caught mismatched arm count\n")
    else:
        print("✗ Failed to catch mismatched arm count\n")
        return False

    # Invalid classification (no primary outcomes)
    invalid_classification_2 = valid_classification.copy()
    invalid_classification_2["num_primary_outcomes"] = 0
    if not classifier.validate_classification(invalid_classification_2):
        print("✓ Caught missing primary outcomes\n")
    else:
        print("✗ Failed to catch missing primary outcomes\n")
        return False

    return True


def test_design_enum_conversion():
    """Test conversion of design strings to TrialDesignType enums."""
    print("=" * 70)
    print("Test 3: Design String to Enum Conversion")
    print("=" * 70)

    classifier = StudyClassifier()

    test_cases = [
        ("parallel", "PARALLEL"),
        ("crossover", "CROSSOVER"),
        ("factorial", "FACTORIAL"),
        ("randomized_controlled_trial", "RCT"),
        ("observational", "OBSERVATIONAL"),
        ("cohort", "COHORT"),
        ("case_control", "CASE_CONTROL"),
        ("cross_sectional", "CROSS_SECTIONAL"),
    ]

    all_passed = True
    for design_str, expected_enum in test_cases:
        result = classifier.get_design_enum(design_str)
        if result.name == expected_enum:
            print(f"✓ '{design_str}' → {result.name}")
        else:
            print(f"✗ '{design_str}' → {result.name} (expected {expected_enum})")
            all_passed = False

    print()
    return all_passed


def test_summary_generation():
    """Test human-readable summary generation."""
    print("=" * 70)
    print("Test 4: Classification Summary Generation")
    print("=" * 70)

    classifier = StudyClassifier()

    classification = {
        "study_type": "randomized_controlled_trial",
        "design": "parallel",
        "num_arms": 2,
        "arm_labels": ["Semaglutide", "Placebo"],
        "num_primary_outcomes": 1,
        "primary_outcome_names": ["Serious cardiovascular events"],
        "num_secondary_outcomes": 3,
        "secondary_outcome_names": ["Body weight change", "GI events", "Discontinuation"],
        "has_safety_analysis": True,
        "has_pharmacokinetic_data": False,
        "follow_up_duration": "40 months",
        "special_design_features": "Multicenter, double-blind",
        "confidence": "high",
        "notes": "SELECT trial",
    }

    summary = classifier.summarize_classification(classification)
    print(summary)
    print()

    return True


def test_outcome_type_flexibility():
    """Test that classifier can handle various outcome configurations."""
    print("=" * 70)
    print("Test 5: Outcome Type Flexibility")
    print("=" * 70)

    classifier = StudyClassifier()

    # Test case 1: Single primary outcome
    single_primary = {
        "study_type": "randomized_controlled_trial",
        "design": "parallel",
        "num_arms": 2,
        "arm_labels": ["A", "B"],
        "num_primary_outcomes": 1,
        "primary_outcome_names": ["Outcome 1"],
        "num_secondary_outcomes": 0,
        "secondary_outcome_names": [],
        "has_safety_analysis": False,
        "has_pharmacokinetic_data": False,
        "follow_up_duration": "12 weeks",
        "special_design_features": "",
        "confidence": "high",
        "notes": "",
    }

    if classifier.validate_classification(single_primary):
        print("✓ Single primary outcome validated")
    else:
        print("✗ Single primary outcome validation failed")
        return False

    # Test case 2: Multiple primary outcomes
    multi_primary = single_primary.copy()
    multi_primary["num_primary_outcomes"] = 3
    multi_primary["primary_outcome_names"] = ["Outcome 1", "Outcome 2", "Outcome 3"]

    if classifier.validate_classification(multi_primary):
        print("✓ Multiple primary outcomes validated")
    else:
        print("✗ Multiple primary outcomes validation failed")
        return False

    # Test case 3: Multiple arms
    multi_arm = single_primary.copy()
    multi_arm["num_arms"] = 4
    multi_arm["arm_labels"] = ["Drug A", "Drug B", "Drug C", "Placebo"]

    if classifier.validate_classification(multi_arm):
        print("✓ Multiple arm configuration validated")
    else:
        print("✗ Multiple arm validation failed")
        return False

    print()
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STUDY CLASSIFIER TESTS")
    print("=" * 70 + "\n")

    results = {
        "JSON Parsing": test_json_parsing(),
        "Classification Validation": test_classification_validation(),
        "Design Enum Conversion": test_design_enum_conversion(),
        "Summary Generation": test_summary_generation(),
        "Outcome Type Flexibility": test_outcome_type_flexibility(),
    }

    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70 + "\n")

    exit(0 if all_passed else 1)
