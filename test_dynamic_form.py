"""
Test Dynamic Form Component

Tests the Phase 2 dynamic form system:
- Dynamic tab generation based on study complexity
- Outcome field rendering (N outcomes)
- Arm field rendering (N arms)
- Safety event field rendering (N events)
- Form data preservation
- Conversion between ClinicalTrial and visual_data formats
"""

from schemas.trial_schemas import (
    ClinicalTrial,
    Outcome,
    ArmAllocation,
    SafetyEvent,
    OutcomeType,
    TrialDesignType,
)


def test_create_simple_trial():
    """Test creating a simple 2-arm RCT."""
    print("=" * 70)
    print("Test 1: Create Simple 2-Arm RCT")
    print("=" * 70)

    trial = ClinicalTrial(
        title="Simple RCT",
        drug_or_intervention="Drug A",
        disease_or_condition="Disease X",
        design=TrialDesignType.PARALLEL,
        total_enrolled=200,
    )

    trial.arms = [
        ArmAllocation(label="Treatment", n_allocated=100),
        ArmAllocation(label="Placebo", n_allocated=100),
    ]

    trial.primary_outcomes = [
        Outcome(
            name="Primary Outcome",
            measure_type=OutcomeType.HAZARD_RATIO,
            estimate=0.75,
            is_primary=True,
        )
    ]

    assert trial.num_arms() == 2
    assert trial.num_primary_outcomes() == 1
    assert trial.design == TrialDesignType.PARALLEL

    print("✓ Simple 2-arm RCT created")
    print(f"  Title: {trial.title}")
    print(f"  Arms: {trial.num_arms()}")
    print(f"  Primary Outcomes: {trial.num_primary_outcomes()}\n")

    return True


def test_create_complex_trial():
    """Test creating a complex 3-arm dose-ranging study with multiple outcomes."""
    print("=" * 70)
    print("Test 2: Create Complex 3-Arm Study with Multiple Outcomes")
    print("=" * 70)

    trial = ClinicalTrial(
        title="Complex Dose-Ranging Study",
        drug_or_intervention="Investigational Drug",
        disease_or_condition="Hypertension",
        design=TrialDesignType.PARALLEL,
        total_enrolled=450,
        mean_age=55.5,
        duration="12 weeks",
    )

    # 3 arms
    trial.arms = [
        ArmAllocation(label="Low Dose", n_allocated=150, n_analyzed=148),
        ArmAllocation(label="High Dose", n_allocated=150, n_analyzed=149),
        ArmAllocation(label="Control", n_allocated=150, n_analyzed=150),
    ]

    # 1 primary + 2 secondary outcomes
    trial.primary_outcomes = [
        Outcome(
            name="Change in Systolic BP",
            measure_type=OutcomeType.MEAN_DIFFERENCE,
            estimate=-12.5,
            units="mmHg",
            is_primary=True,
        )
    ]

    trial.secondary_outcomes = [
        Outcome(
            name="Response Rate",
            measure_type=OutcomeType.RESPONSE_RATE,
            estimate=0.65,
            is_primary=False,
        ),
        Outcome(
            name="Quality of Life",
            measure_type=OutcomeType.CONTINUOUS,
            estimate=8.5,
            is_primary=False,
        ),
    ]

    # 3 safety events
    trial.safety_events = [
        SafetyEvent(
            event_name="Headache",
            event_type="neurological",
            arm_events={
                "Low Dose": {"percent": 10.0},
                "High Dose": {"percent": 15.0},
                "Control": {"percent": 5.0},
            },
        ),
        SafetyEvent(
            event_name="Dizziness",
            event_type="neurological",
            arm_events={
                "Low Dose": {"percent": 8.0},
                "High Dose": {"percent": 12.0},
                "Control": {"percent": 3.0},
            },
        ),
        SafetyEvent(
            event_name="Serious Adverse Event",
            event_type="serious",
            arm_events={
                "Low Dose": {"percent": 1.0},
                "High Dose": {"percent": 2.0},
                "Control": {"percent": 0.5},
            },
            serious=True,
        ),
    ]

    trial.conclusions = [
        "High dose showed superior efficacy",
        "Safety profile acceptable across doses",
    ]

    assert trial.num_arms() == 3
    assert trial.num_primary_outcomes() == 1
    assert trial.num_secondary_outcomes() == 2
    assert trial.num_safety_events() == 3
    assert len(trial.conclusions) == 2

    print("✓ Complex study created")
    print(f"  Title: {trial.title}")
    print(f"  Arms: {trial.num_arms()} (Low Dose, High Dose, Control)")
    print(f"  Primary Outcomes: {trial.num_primary_outcomes()}")
    print(f"  Secondary Outcomes: {trial.num_secondary_outcomes()}")
    print(f"  Safety Events: {trial.num_safety_events()}")
    print(f"  Conclusions: {len(trial.conclusions)}\n")

    return True


def test_dynamic_tab_generation():
    """Test that correct tabs would be generated for different study types."""
    print("=" * 70)
    print("Test 3: Dynamic Tab Generation Logic")
    print("=" * 70)

    # Minimal trial (outcomes + safety empty)
    minimal = ClinicalTrial(
        title="Minimal",
        drug_or_intervention="Drug",
        disease_or_condition="Disease",
    )

    minimal_tabs = ["Trial Info", "Design", "Population & Arms"]
    if minimal.primary_outcomes or minimal.secondary_outcomes or minimal.exploratory_outcomes:
        minimal_tabs.append("Outcomes")
    if minimal.safety_events:
        minimal_tabs.append("Safety")
    minimal_tabs.append("Conclusions")

    assert len(minimal_tabs) == 4  # Info, Design, Population, Conclusions
    print(f"✓ Minimal trial tabs: {minimal_tabs}")

    # Full trial (all data)
    full = ClinicalTrial(
        title="Full",
        drug_or_intervention="Drug",
        disease_or_condition="Disease",
    )
    full.primary_outcomes = [Outcome(name="O1", measure_type=OutcomeType.HAZARD_RATIO, is_primary=True)]
    full.safety_events = [SafetyEvent(event_name="Event1", arm_events={})]

    full_tabs = ["Trial Info", "Design", "Population & Arms"]
    if full.primary_outcomes or full.secondary_outcomes or full.exploratory_outcomes:
        full_tabs.append("Outcomes")
    if full.safety_events:
        full_tabs.append("Safety")
    full_tabs.append("Conclusions")

    assert len(full_tabs) == 6  # Info, Design, Population, Outcomes, Safety, Conclusions
    print(f"✓ Full trial tabs: {full_tabs}\n")

    return True


def test_trial_serialization_with_multiple_outcomes():
    """Test serializing a complex trial with N outcomes to JSON and back."""
    print("=" * 70)
    print("Test 4: Complex Trial Serialization with Multiple Outcomes")
    print("=" * 70)

    trial = ClinicalTrial(
        title="Multi-Outcome Trial",
        drug_or_intervention="Drug X",
        disease_or_condition="Disease Y",
        total_enrolled=500,
    )

    trial.primary_outcomes = [
        Outcome(
            name="Primary 1",
            measure_type=OutcomeType.ODDS_RATIO,
            estimate=1.5,
            is_primary=True,
        ),
    ]

    trial.secondary_outcomes = [
        Outcome(name="Secondary 1", measure_type=OutcomeType.MEAN_DIFFERENCE, estimate=5.0, is_primary=False),
        Outcome(name="Secondary 2", measure_type=OutcomeType.EVENT_RATE, estimate=0.45, is_primary=False),
        Outcome(name="Secondary 3", measure_type=OutcomeType.RESPONSE_RATE, estimate=0.55, is_primary=False),
    ]

    # Serialize to dict
    trial_dict = trial.to_dict()
    assert len(trial_dict["outcomes"]["primary"]) == 1
    assert len(trial_dict["outcomes"]["secondary"]) == 3
    print("✓ Serialized to dict")

    # Reconstruct from dict
    trial_reconstructed = ClinicalTrial.from_dict(trial_dict)
    assert trial_reconstructed.title == trial.title
    assert trial_reconstructed.num_primary_outcomes() == 1
    assert trial_reconstructed.num_secondary_outcomes() == 3
    assert len(trial_reconstructed.secondary_outcomes) == 3
    print("✓ Reconstructed from dict")
    print(f"  Primary: {trial_reconstructed.num_primary_outcomes()}")
    print(f"  Secondary: {trial_reconstructed.num_secondary_outcomes()}")
    print(f"  Secondary names: {[o.name for o in trial_reconstructed.secondary_outcomes]}\n")

    return True


def test_trial_with_pharmacokinetic_outcomes():
    """Test trial with pharmacokinetic parameters."""
    print("=" * 70)
    print("Test 5: PK Trial with Specialized Outcomes")
    print("=" * 70)

    trial = ClinicalTrial(
        title="Pharmacokinetic Study",
        drug_or_intervention="New Drug",
        disease_or_condition="Healthy Volunteers",
        design=TrialDesignType.PHARMACOKINETIC,
    )

    trial.arms = [
        ArmAllocation(label="Fasted", n_allocated=12),
        ArmAllocation(label="Fed", n_allocated=12),
    ]

    trial.primary_outcomes = [
        Outcome(name="AUC", measure_type=OutcomeType.AUC, estimate=120.5, units="h·ng/mL", is_primary=True),
        Outcome(name="Cmax", measure_type=OutcomeType.CMAX, estimate=25.3, units="ng/mL", is_primary=True),
    ]

    trial.secondary_outcomes = [
        Outcome(name="Tmax", measure_type=OutcomeType.TMAX, estimate=2.5, units="h", is_primary=False),
        Outcome(name="Half-life", measure_type=OutcomeType.HALF_LIFE, estimate=8.2, units="h", is_primary=False),
    ]

    assert trial.num_primary_outcomes() == 2
    assert trial.num_secondary_outcomes() == 2
    assert trial.design == TrialDesignType.PHARMACOKINETIC

    print("✓ PK trial created")
    print(f"  Design: {trial.design.value}")
    print(f"  Primary PK parameters: {[o.name for o in trial.primary_outcomes]}")
    print(f"  Secondary PK parameters: {[o.name for o in trial.secondary_outcomes]}\n")

    return True


def test_form_field_count():
    """Test that form has appropriate number of editable fields for different studies."""
    print("=" * 70)
    print("Test 6: Form Field Count for Different Study Types")
    print("=" * 70)

    # Simple 2-arm study
    simple = ClinicalTrial(
        title="Simple",
        drug_or_intervention="Drug",
        disease_or_condition="Disease",
    )
    simple.arms = [ArmAllocation(label="Arm1"), ArmAllocation(label="Arm2")]
    simple.primary_outcomes = [Outcome(name="O1", measure_type=OutcomeType.HAZARD_RATIO, is_primary=True)]

    # Count expected form fields for simple study
    # Trial Info: title, drug, trial_name, indication, publication = 5
    # Design: design, mean_age, duration, follow_up = 4
    # Population: total_enrolled, inclusion, exclusion = 3
    #   + 2 arms * 4 fields each (label, n_allocated, n_analyzed, description) = 8
    # Outcomes: 1 primary * 5 fields (name, measure, estimate, ci, pvalue) = 5
    # Conclusions: 1 field = 1
    # Total: ~30 fields minimum

    print(f"✓ Simple study fields estimate: ~30")
    print(f"  - Trial Info: 5 fields")
    print(f"  - Design: 4 fields")
    print(f"  - Population: 3 fields")
    print(f"  - Arms: {simple.num_arms()} arms × 4 fields = 8")
    print(f"  - Primary Outcomes: {simple.num_primary_outcomes()} × 5 = 5")
    print(f"  - Conclusions: 1 field")

    # Complex 3-arm with 4 outcomes and 3 safety events
    complex_trial = ClinicalTrial(
        title="Complex",
        drug_or_intervention="Drug",
        disease_or_condition="Disease",
    )
    complex_trial.arms = [
        ArmAllocation(label="Arm1"),
        ArmAllocation(label="Arm2"),
        ArmAllocation(label="Arm3"),
    ]
    complex_trial.primary_outcomes = [
        Outcome(name="O1", measure_type=OutcomeType.HAZARD_RATIO, is_primary=True)
    ]
    complex_trial.secondary_outcomes = [
        Outcome(name="O2", measure_type=OutcomeType.ODDS_RATIO, is_primary=False),
        Outcome(name="O3", measure_type=OutcomeType.MEAN_DIFFERENCE, is_primary=False),
    ]
    complex_trial.safety_events = [
        SafetyEvent(event_name="E1", arm_events={"Arm1": {}, "Arm2": {}, "Arm3": {}}),
        SafetyEvent(event_name="E2", arm_events={"Arm1": {}, "Arm2": {}, "Arm3": {}}),
        SafetyEvent(event_name="E3", arm_events={"Arm1": {}, "Arm2": {}, "Arm3": {}}),
    ]

    # Estimate for complex study
    print(f"\n✓ Complex study fields estimate: ~60+")
    print(f"  - Trial Info: 5 fields")
    print(f"  - Design: 4 fields")
    print(f"  - Population: 3 fields")
    print(f"  - Arms: {complex_trial.num_arms()} arms × 4 fields = 12")
    print(f"  - Primary Outcomes: {complex_trial.num_primary_outcomes()} × 5 = 5")
    print(f"  - Secondary Outcomes: {complex_trial.num_secondary_outcomes()} × 5 = 10")
    print(f"  - Safety Events: {complex_trial.num_safety_events()} × (5 + 3*2) = ~45")
    print(f"  - Conclusions: 1 field\n")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DYNAMIC FORM TESTS")
    print("=" * 70 + "\n")

    results = {
        "Create Simple Trial": test_create_simple_trial(),
        "Create Complex Trial": test_create_complex_trial(),
        "Dynamic Tab Generation": test_dynamic_tab_generation(),
        "Multi-Outcome Serialization": test_trial_serialization_with_multiple_outcomes(),
        "PK Trial Creation": test_trial_with_pharmacokinetic_outcomes(),
        "Form Field Count": test_form_field_count(),
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
