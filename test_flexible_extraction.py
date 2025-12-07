"""
Test Flexible Extraction Pipeline

Tests the Phase 2 flexible extraction system:
- Study classification
- Flexible outcome extraction
- Flexible safety event extraction
- Flexible arm extraction
- Schema mapping to ClinicalTrial objects
"""

import json
from utils.schema_mapper import SchemaMapper
from schemas.trial_schemas import ClinicalTrial, OutcomeType, TrialDesignType


def test_schema_mapper_outcome():
    """Test mapping outcome data to Outcome object."""
    print("=" * 70)
    print("Test 1: Schema Mapper - Outcome Mapping")
    print("=" * 70)

    outcome_data = {
        "name": "Serious Cardiovascular Events",
        "measure_type": "hazard_ratio",
        "estimate": 0.72,
        "confidence_interval": {"lower": 0.55, "upper": 0.94},
        "p_value": 0.016,
        "units": None,
        "is_primary": True,
    }

    outcome = SchemaMapper.map_outcome(outcome_data, is_primary=True)

    assert outcome.name == "Serious Cardiovascular Events"
    assert outcome.measure_type == OutcomeType.HAZARD_RATIO
    assert outcome.estimate == 0.72
    assert outcome.confidence_interval.lower == 0.55
    assert outcome.confidence_interval.upper == 0.94
    assert outcome.p_value == 0.016
    assert outcome.is_primary is True

    print("✓ Outcome mapping successful")
    print(f"  Name: {outcome.name}")
    print(f"  Measure: {outcome.measure_type.value}")
    print(f"  Estimate: {outcome.estimate}")
    print(f"  CI: {outcome.confidence_interval}")
    print(f"  P-value: {outcome.p_value}\n")

    return True


def test_schema_mapper_arm():
    """Test mapping arm data to ArmAllocation object."""
    print("=" * 70)
    print("Test 2: Schema Mapper - Arm Allocation Mapping")
    print("=" * 70)

    arm_data = {
        "label": "Semaglutide 2.4 mg",
        "n_allocated": 1174,
        "n_analyzed": 1168,
        "n_completed": 1118,
        "description": "Weekly semaglutide injection",
    }

    arm = SchemaMapper.map_arm(arm_data)

    assert arm.label == "Semaglutide 2.4 mg"
    assert arm.n_allocated == 1174
    assert arm.n_analyzed == 1168
    assert arm.n_completed == 1118

    print("✓ Arm allocation mapping successful")
    print(f"  Label: {arm.label}")
    print(f"  Allocated: {arm.n_allocated}")
    print(f"  Analyzed: {arm.n_analyzed}")
    print(f"  Completed: {arm.n_completed}\n")

    return True


def test_schema_mapper_safety_event():
    """Test mapping safety event data to SafetyEvent object."""
    print("=" * 70)
    print("Test 3: Schema Mapper - Safety Event Mapping")
    print("=" * 70)

    event_data = {
        "event_name": "Nausea",
        "event_type": "gastrointestinal",
        "arm_data": {
            "Semaglutide": {"percent": 24.6, "count": 288},
            "Placebo": {"percent": 5.4, "count": 32},
        },
        "serious": False,
        "led_to_discontinuation": False,
        "notes": "Most common adverse event",
    }

    event = SchemaMapper.map_safety_event(event_data)

    assert event.event_name == "Nausea"
    assert event.event_type == "gastrointestinal"
    assert event.serious is False
    assert "Semaglutide" in event.arm_events
    assert event.arm_events["Semaglutide"]["percent"] == 24.6

    print("✓ Safety event mapping successful")
    print(f"  Event: {event.event_name}")
    print(f"  Type: {event.event_type}")
    print(f"  Semaglutide: {event.arm_events['Semaglutide']['percent']}%")
    print(f"  Placebo: {event.arm_events['Placebo']['percent']}%\n")

    return True


def test_create_clinical_trial():
    """Test creating complete ClinicalTrial object from extracted components."""
    print("=" * 70)
    print("Test 4: Create Clinical Trial from Components")
    print("=" * 70)

    # Simulated extracted data
    study_classification = {
        "study_type": "randomized_controlled_trial",
        "design": "parallel",
        "num_arms": 2,
        "arm_labels": ["Semaglutide", "Placebo"],
        "num_primary_outcomes": 1,
        "primary_outcome_names": ["Serious Cardiovascular Events"],
        "num_secondary_outcomes": 2,
        "follow_up_duration": "40 months",
    }

    outcomes_data = {
        "outcomes": [
            {
                "name": "Serious Cardiovascular Events",
                "measure_type": "hazard_ratio",
                "estimate": 0.72,
                "confidence_interval": {"lower": 0.55, "upper": 0.94},
                "p_value": 0.016,
                "is_primary": True,
            },
            {
                "name": "Body Weight Change",
                "measure_type": "mean_difference",
                "estimate": -4.2,
                "units": "kg",
                "is_primary": False,
            },
        ]
    }

    arms_data = {
        "arms": [
            {
                "label": "Semaglutide 2.4 mg",
                "n_allocated": 1174,
                "n_analyzed": 1168,
                "description": "Weekly injection",
            },
            {
                "label": "Placebo",
                "n_allocated": 586,
                "n_analyzed": 583,
                "description": "Weekly placebo injection",
            },
        ]
    }

    safety_data = {
        "safety_events": [
            {
                "event_name": "Nausea",
                "event_type": "gastrointestinal",
                "arm_data": {"Semaglutide": {"percent": 24.6}, "Placebo": {"percent": 5.4}},
                "serious": False,
            }
        ]
    }

    trial = SchemaMapper.create_clinical_trial(
        title="SELECT Trial",
        drug_or_intervention="Semaglutide",
        disease_or_condition="Cardiovascular disease risk reduction in overweight/obese patients",
        outcomes_data=outcomes_data,
        arms_data=arms_data,
        safety_data=safety_data,
        study_classification=study_classification,
        trial_name="SELECT",
        conclusions=["Semaglutide significantly reduces cardiovascular risk"],
    )

    assert trial.title == "SELECT Trial"
    assert trial.drug_or_intervention == "Semaglutide"
    assert trial.num_arms() == 2
    assert trial.num_primary_outcomes() == 1
    assert trial.num_secondary_outcomes() == 1
    assert trial.num_safety_events() == 1
    assert trial.design == TrialDesignType.PARALLEL

    print("✓ Clinical trial creation successful")
    print(f"  Title: {trial.title}")
    print(f"  Drug: {trial.drug_or_intervention}")
    print(f"  Design: {trial.design.value}")
    print(f"  Arms: {trial.num_arms()} ({', '.join([a.label for a in trial.arms])})")
    print(f"  Primary Outcomes: {trial.num_primary_outcomes()}")
    print(f"  Secondary Outcomes: {trial.num_secondary_outcomes()}")
    print(f"  Safety Events: {trial.num_safety_events()}")
    print(f"  Conclusions: {len(trial.conclusions)}\n")

    return True


def test_trial_serialization():
    """Test ClinicalTrial serialization to/from JSON."""
    print("=" * 70)
    print("Test 5: Clinical Trial JSON Serialization")
    print("=" * 70)

    # Create a trial
    outcomes_data = {
        "outcomes": [
            {
                "name": "Primary Outcome",
                "measure_type": "odds_ratio",
                "estimate": 1.5,
                "is_primary": True,
            }
        ]
    }

    arms_data = {
        "arms": [
            {"label": "Treatment", "n_allocated": 100},
            {"label": "Control", "n_allocated": 100},
        ]
    }

    trial = SchemaMapper.create_clinical_trial(
        title="Test Trial",
        drug_or_intervention="Test Drug",
        disease_or_condition="Test Disease",
        outcomes_data=outcomes_data,
        arms_data=arms_data,
    )

    # Convert to dict
    trial_dict = trial.to_dict()
    print("✓ Serialized to JSON")

    # Reconstruct from dict
    trial_reconstructed = ClinicalTrial.from_dict(trial_dict)
    assert trial_reconstructed.title == trial.title
    assert trial_reconstructed.num_arms() == trial.num_arms()
    assert trial_reconstructed.num_primary_outcomes() == trial.num_primary_outcomes()

    print("✓ Deserialized from JSON")
    print(f"  JSON keys: {list(trial_dict.keys())}")
    print(f"  Reconstructed title: {trial_reconstructed.title}")
    print(f"  Round-trip successful\n")

    return True


def test_flexible_multiarmed_trial():
    """Test handling of trial with 3+ arms."""
    print("=" * 70)
    print("Test 6: Flexible Multi-Armed Trial (3 arms)")
    print("=" * 70)

    outcomes_data = {
        "outcomes": [
            {
                "name": "Primary Endpoint",
                "measure_type": "mean_difference",
                "estimate": 5.2,
                "is_primary": True,
            },
            {
                "name": "Secondary 1",
                "measure_type": "percentage",
                "estimate": 45.0,
                "is_primary": False,
            },
            {
                "name": "Secondary 2",
                "measure_type": "event_rate",
                "estimate": 0.25,
                "is_primary": False,
            },
        ]
    }

    arms_data = {
        "arms": [
            {"label": "Low Dose", "n_allocated": 150},
            {"label": "High Dose", "n_allocated": 150},
            {"label": "Control", "n_allocated": 150},
        ]
    }

    safety_data = {
        "safety_events": [
            {
                "event_name": "Headache",
                "event_type": "neurological",
                "arm_data": {
                    "Low Dose": {"percent": 10.0},
                    "High Dose": {"percent": 15.0},
                    "Control": {"percent": 5.0},
                },
                "serious": False,
            },
            {
                "event_name": "Serious Adverse Event",
                "event_type": "serious",
                "arm_data": {
                    "Low Dose": {"percent": 1.0},
                    "High Dose": {"percent": 2.0},
                    "Control": {"percent": 0.5},
                },
                "serious": True,
            },
        ]
    }

    trial = SchemaMapper.create_clinical_trial(
        title="Three-Arm Dose Ranging Study",
        drug_or_intervention="Investigational Drug",
        disease_or_condition="Hypertension",
        outcomes_data=outcomes_data,
        arms_data=arms_data,
        safety_data=safety_data,
    )

    assert trial.num_arms() == 3
    assert trial.num_primary_outcomes() == 1
    assert trial.num_secondary_outcomes() == 2
    assert trial.num_safety_events() == 2

    print("✓ Three-armed trial created successfully")
    print(f"  Arms: {trial.num_arms()}")
    for arm in trial.arms:
        print(f"    - {arm.label}: N={arm.n_allocated}")
    print(f"  Primary Outcomes: {trial.num_primary_outcomes()}")
    print(f"  Secondary Outcomes: {trial.num_secondary_outcomes()}")
    print(f"  Safety Events: {trial.num_safety_events()}")
    print()

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FLEXIBLE EXTRACTION TESTS")
    print("=" * 70 + "\n")

    results = {
        "Outcome Mapping": test_schema_mapper_outcome(),
        "Arm Allocation Mapping": test_schema_mapper_arm(),
        "Safety Event Mapping": test_schema_mapper_safety_event(),
        "Clinical Trial Creation": test_create_clinical_trial(),
        "JSON Serialization": test_trial_serialization(),
        "Multi-Armed Trial": test_flexible_multiarmed_trial(),
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
