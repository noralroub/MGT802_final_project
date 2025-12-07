# Phase 2: Flexible Field Population - Detailed Implementation Plan

**Status**: Ready to Start
**Estimated Timeline**: 8-12 hours (1-2 days)
**Priority**: HIGH - Addresses core extraction quality issues

---

## Overview

Phase 2 transforms the extraction pipeline from **Semaglutide-specific** to **trial-agnostic**. Instead of assuming fixed trial structures, the system will:

1. Auto-detect trial type and design
2. Extract outcomes dynamically (N primary, N secondary)
3. Support diverse trial structures (parallel, crossover, factorial, etc.)
4. Handle different outcome types (HR, OR, RR, mean differences, event rates, etc.)
5. Scale editable form based on actual trial complexity

---

## Problem Statement

### Current State (Phase 1 End)
- Extraction assumes Semaglutide trial structure
- Fixed schemas: 1 primary outcome, 2 arms, specific adverse event types
- Hardcoded regex patterns for Semaglutide-specific metrics
- Works well for cardiovascular RCTs, fails on other trial types
- Users must manually correct extraction for non-standard trials

### Desired State (Phase 2 End)
- Works for ANY trial type (RCT, observational, crossover, pharmacokinetic, etc.)
- Any number of outcomes and arms
- Extracts all safety events (not just predefined categories)
- Adapts to trial complexity automatically
- Users see form fields that match their specific trial

---

## Architecture Changes

### Current Data Flow (Phase 1)
```
PDF → RAG → hardcoded LLM prompts → fixed schema → fixed template
```

### New Data Flow (Phase 2)
```
PDF → RAG → Trial Classifier → Flexible Extraction → Flexible Schema → Adaptive Editable Form
```

---

## Implementation Steps

### Step 1: Design Flexible Schemas

**File to Create**: `schemas/trial_schemas.py`

```python
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

class OutcomeType(str, Enum):
    """Types of outcome measures"""
    HAZARD_RATIO = "hazard_ratio"
    ODDS_RATIO = "odds_ratio"
    RELATIVE_RISK = "relative_risk"
    MEAN_DIFFERENCE = "mean_difference"
    STANDARDIZED_MEAN_DIFF = "standardized_mean_difference"
    EVENT_RATE = "event_rate"
    PERCENTAGE = "percentage"
    CONTINUOUS = "continuous"  # Generic for other measurements

class TrialDesignType(str, Enum):
    """Trial design types"""
    RCT = "randomized_controlled_trial"
    PARALLEL = "parallel"
    CROSSOVER = "crossover"
    FACTORIAL = "factorial"
    OBSERVATIONAL = "observational"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    PHARMACOKINETIC = "pharmacokinetic"

@dataclass
class ConfidenceInterval:
    """Represents confidence interval"""
    lower: Optional[float] = None
    upper: Optional[float] = None
    level: float = 0.95  # 95%, 90%, etc.

    def __str__(self) -> str:
        if self.lower and self.upper:
            return f"({self.lower:.2f}-{self.upper:.2f})"
        return "n/a"

@dataclass
class Outcome:
    """Generic outcome structure - works for ANY trial"""
    name: str
    measure_type: OutcomeType
    estimate: Optional[float] = None  # HR, OR, RR, mean diff, etc.
    confidence_interval: Optional[ConfidenceInterval] = None
    p_value: Optional[float] = None
    units: Optional[str] = None
    definition: Optional[str] = None
    is_primary: bool = False

@dataclass
class ArmAllocation:
    """Participant allocation to trial arm"""
    label: str
    n_allocated: Optional[int] = None
    n_analyzed: Optional[int] = None
    description: Optional[str] = None

@dataclass
class EventRate:
    """Event rate for an arm (used in outcome analysis)"""
    label: str
    percent: Optional[float] = None
    count: Optional[int] = None
    denominator: Optional[int] = None

@dataclass
class SafetyEvent:
    """Flexible adverse event/safety data"""
    event_name: str
    event_type: Optional[str] = None  # e.g., "gastrointestinal", "serious", "discontinued"
    arm_events: dict = field(default_factory=dict)  # {arm_label: event_rate}
    serious: bool = False
    led_to_discontinuation: bool = False
    notes: Optional[str] = None

@dataclass
class Dosing:
    """Dosing/treatment information"""
    description: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    adjustments: Optional[str] = None

@dataclass
class ClinicalTrial:
    """Flexible trial structure that adapts to ANY trial type"""

    # Identifiers
    title: str
    trial_name: Optional[str] = None
    drug_or_intervention: str
    disease_or_condition: str
    publication: Optional[str] = None

    # Design
    design: TrialDesignType

    # Population
    total_enrolled: Optional[int] = None
    arms: List[ArmAllocation] = field(default_factory=list)
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None

    # Demographics
    mean_age: Optional[float] = None
    age_range: Optional[str] = None
    gender_distribution: Optional[str] = None

    # Outcomes - FLEXIBLE (N primary + N secondary)
    primary_outcomes: List[Outcome] = field(default_factory=list)
    secondary_outcomes: List[Outcome] = field(default_factory=list)
    exploratory_outcomes: List[Outcome] = field(default_factory=list)

    # Safety - FLEXIBLE (any number of events)
    safety_events: List[SafetyEvent] = field(default_factory=list)

    # Treatment/Dosing
    dosing: Optional[Dosing] = None

    # Results and Conclusions
    conclusions: List[str] = field(default_factory=list)

    # Metadata
    duration: Optional[str] = None
    follow_up_period: Optional[str] = None

    def num_primary_outcomes(self) -> int:
        return len(self.primary_outcomes)

    def num_secondary_outcomes(self) -> int:
        return len(self.secondary_outcomes)

    def num_arms(self) -> int:
        return len(self.arms)

    def num_safety_events(self) -> int:
        return len(self.safety_events)
```

**Why This Design:**
- Fully flexible: works with 1 or 100 outcomes
- Type-safe: Enums prevent invalid values
- Extensible: Can add new OutcomeTypes without breaking code
- Dataclass: Easy serialization, clean API

---

### Step 2: Create Trial Classifier Agent

**File to Create**: `agents/trial_classifier.py`

```python
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from config import OPENAI_API_KEY
from core.retrieval import RAGPipeline
from schemas.trial_schemas import TrialDesignType, ClinicalTrial

logger = logging.getLogger(__name__)

class TrialClassifier:
    """
    Classifies trial type and structure from PDF.

    This agent answers: "What type of trial is this, and what should
    I be extracting?"
    """

    def __init__(self, model: str = "gpt-4", top_k: int = 8):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.top_k = top_k
        self.pipeline = RAGPipeline(collection_name="medical_papers")

    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
            return json.loads(text)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise

    def classify_trial(self, context: str) -> Dict[str, Any]:
        """
        Classify trial and extract structural information.

        Returns:
        {
            "trial_type": "randomized_controlled_trial",
            "design": "parallel",
            "num_arms": 2,
            "arm_labels": ["Semaglutide", "Placebo"],
            "num_primary_outcomes": 1,
            "primary_outcome_names": ["Serious cardiovascular events"],
            "num_secondary_outcomes": 5,
            "has_safety_analysis": true,
            "follow_up_duration": "40 months",
            "special_notes": "..."
        }
        """

        system_prompt = """You are an expert clinical trial analyst.
Classify the trial type and structure. Return ONLY valid JSON with no commentary."""

        user_prompt = """Classify this trial:

1. What is the trial TYPE? (randomized_controlled_trial, observational, crossover, etc.)
2. What is the DESIGN? (parallel, factorial, crossover, etc.)
3. How many TREATMENT ARMS? List them.
4. How many PRIMARY OUTCOMES? What are they?
5. How many SECONDARY OUTCOMES? List them.
6. Are there SAFETY outcomes?
7. What is the FOLLOW-UP DURATION?

Return JSON:
{
  "trial_type": "...",
  "design": "...",
  "num_arms": 0,
  "arm_labels": ["..."],
  "num_primary_outcomes": 0,
  "primary_outcome_names": ["..."],
  "num_secondary_outcomes": 0,
  "secondary_outcome_names": ["..."],
  "has_safety_analysis": false,
  "has_pharmacokinetic_data": false,
  "follow_up_duration": "...",
  "special_design_features": "...",
  "confidence": "high|medium|low"
}"""

        context = self.pipeline.get_context(
            "trial design type structure arms outcomes follow-up",
            top_k=self.top_k
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n\nCONTEXT:\n{context}"},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
        )

        return self._safe_json_parse(response.choices[0].message.content)

```

**What This Does:**
- Queries RAG for trial design information
- Asks Claude to classify trial type
- Returns structure metadata (num outcomes, num arms, etc.)
- Guides downstream extraction

---

### Step 3: Refactor Extraction Agent

**File to Modify**: `agents/extraction_agent.py`

**Key Changes:**

1. **Add trial classifier step**:
```python
def run_full_extraction(self, pdf_path: str) -> Dict[str, Any]:
    """End-to-end extraction with trial classification"""

    self.ingest_pdf(pdf_path)

    # NEW: Classify trial first
    classifier = TrialClassifier(model=self.model)
    trial_classification = classifier.classify_trial(pdf_context)

    # Extract based on classification
    picot = self.extract_picot()
    stats = self.extract_stats()
    limitations = self.extract_limitations()

    # NEW: Extract flexible outcomes
    outcomes = self.extract_outcomes_flexible(trial_classification)

    # NEW: Extract flexible safety events
    safety_events = self.extract_safety_events_flexible(trial_classification)

    return {
        "trial_classification": trial_classification,
        "picot": picot,
        "stats": stats,
        "limitations": limitations,
        "outcomes": outcomes,
        "safety_events": safety_events,
        "structured_abstract": self.generate_structured_abstract(...),
        "trial_data": self.generate_trial_data(...)
    }
```

2. **Replace hardcoded prompts with flexible extraction**:

```python
def extract_outcomes_flexible(self, trial_classification: Dict) -> List[Dict]:
    """
    Extract N outcomes dynamically based on trial classification.

    Not hardcoded for specific outcomes like "Semaglutide", "body weight", etc.
    Instead, asks Claude to find whatever outcomes exist in the paper.
    """

    num_primary = trial_classification.get("num_primary_outcomes", 1)
    num_secondary = trial_classification.get("num_secondary_outcomes", 0)

    # Build prompt asking for ALL outcomes
    user_prompt = f"""Extract ALL outcomes from this trial.

Expected structure:
- {num_primary} PRIMARY outcome(s)
- {num_secondary} SECONDARY outcome(s)

For each outcome, extract:
- Name/Label
- Measure type (Hazard Ratio, Odds Ratio, Event Rate, etc.)
- Estimate (the numerical value)
- 95% Confidence Interval
- P-value
- Units (if applicable)
- Definition (how it was defined)

Return JSON:
{{
  "primary_outcomes": [
    {{
      "name": "...",
      "measure_type": "...",
      "estimate": 0.0,
      "ci_lower": 0.0,
      "ci_upper": 0.0,
      "p_value": 0.0,
      "units": "...",
      "definition": "..."
    }}
  ],
  "secondary_outcomes": [...]
}}"""

    context = self.pipeline.get_context(
        "outcomes results primary secondary hazard ratio odds ratio event rate",
        top_k=self.top_k
    )

    return self._run_extraction(
        query="all outcomes primary secondary results",
        system_prompt="Extract ALL trial outcomes. Return ONLY JSON.",
        user_prompt=user_prompt
    )
```

3. **Extract flexible safety events**:

```python
def extract_safety_events_flexible(self, trial_classification: Dict) -> List[Dict]:
    """
    Extract any safety events mentioned, not just predefined categories.
    """

    user_prompt = """Extract ALL adverse events and safety data mentioned.

For each event, extract:
- Event name (e.g., "Nausea", "Myocardial infarction", "Serious adverse events")
- Rates or counts for each arm
- Was it serious?
- Did it lead to discontinuation?
- Any special notes

Return JSON:
{
  "safety_events": [
    {
      "name": "...",
      "serious": false,
      "discontinuation": false,
      "arm_data": {
        "arm_1_label": {"percent": 0.0, "count": 0},
        "arm_2_label": {"percent": 0.0, "count": 0}
      }
    }
  ]
}"""

    context = self.pipeline.get_context(
        "adverse events safety side effects discontinuation serious",
        top_k=self.top_k
    )

    return self._run_extraction(
        query="adverse events safety all side effects",
        system_prompt="Extract ALL adverse events. Return ONLY JSON.",
        user_prompt=user_prompt
    )
```

---

### Step 4: Create Schema Mapper

**File to Create**: `utils/schema_mapper.py`

Maps from LLM output (flexible) → Dataclass (type-safe) → Editable form

```python
from typing import Dict, Any, List
from schemas.trial_schemas import (
    ClinicalTrial, Outcome, ArmAllocation, SafetyEvent,
    Dosing, OutcomeType, TrialDesignType, ConfidenceInterval
)

class TrialSchemaMapper:
    """Maps extraction output to typed ClinicalTrial dataclass"""

    @staticmethod
    def map_from_extraction(
        trial_classification: Dict,
        picot: Dict,
        outcomes: Dict,
        safety_events: Dict,
        other_data: Dict
    ) -> ClinicalTrial:
        """Build typed ClinicalTrial from extraction outputs"""

        # Map trial identifiers
        trial = ClinicalTrial(
            title=other_data.get("trial_info", {}).get("title", "Unknown"),
            trial_name=trial_classification.get("trial_acronym"),
            drug_or_intervention=other_data.get("trial_info", {}).get("drug", ""),
            disease_or_condition=picot.get("population", {}).get("indication", ""),
            design=TrialDesignType(trial_classification.get("design", "parallel")),
        )

        # Map arms
        for arm_label in trial_classification.get("arm_labels", []):
            trial.arms.append(
                ArmAllocation(
                    label=arm_label,
                    n_allocated=None  # Will be filled from PICOT
                )
            )

        # Map primary outcomes
        for outcome_data in outcomes.get("primary_outcomes", []):
            trial.primary_outcomes.append(
                Outcome(
                    name=outcome_data.get("name", ""),
                    measure_type=OutcomeType(outcome_data.get("measure_type")),
                    estimate=outcome_data.get("estimate"),
                    confidence_interval=ConfidenceInterval(
                        lower=outcome_data.get("ci_lower"),
                        upper=outcome_data.get("ci_upper")
                    ),
                    p_value=outcome_data.get("p_value"),
                    is_primary=True
                )
            )

        # Map secondary outcomes
        for outcome_data in outcomes.get("secondary_outcomes", []):
            trial.secondary_outcomes.append(
                Outcome(
                    name=outcome_data.get("name", ""),
                    measure_type=OutcomeType(outcome_data.get("measure_type")),
                    estimate=outcome_data.get("estimate"),
                    is_primary=False
                )
            )

        # Map safety events
        for event_data in safety_events.get("safety_events", []):
            trial.safety_events.append(
                SafetyEvent(
                    event_name=event_data.get("name", ""),
                    serious=event_data.get("serious", False),
                    led_to_discontinuation=event_data.get("discontinuation", False),
                    arm_events=event_data.get("arm_data", {})
                )
            )

        return trial
```

---

### Step 5: Update Editable Form to Scale Dynamically

**File to Modify**: `ui/editable_abstract.py`

Add dynamic field generation:

```python
class EditableAbstractForm:

    @staticmethod
    def render_edit_form_dynamic(trial_data: ClinicalTrial) -> ClinicalTrial:
        """
        Render form that ADAPTS to trial complexity.

        Instead of fixed 4 tabs, generates tabs based on what's in the trial.
        """

        st.session_state.editable_trial_data = trial_data.copy()

        # Build tabs dynamically
        num_outcomes = trial_data.num_primary_outcomes() + trial_data.num_secondary_outcomes()
        num_safety = trial_data.num_safety_events()

        tab_list = ["Trial Info", "Population"]

        if num_outcomes > 0:
            tab_list.append(f"Outcomes ({num_outcomes})")

        if num_safety > 0:
            tab_list.append(f"Safety ({num_safety})")

        tab_list.append("Conclusions")

        tabs = st.tabs(tab_list)

        # Tab 1: Trial Info (always present)
        with tabs[0]:
            # Render trial info fields
            pass

        # Tab 2: Population (always present)
        with tabs[1]:
            # Render population fields
            # DYNAMIC: Render all arms (not just 2!)
            for idx, arm in enumerate(trial_data.arms):
                st.text_input(f"Arm {idx+1} Label", value=arm.label)
                st.number_input(f"Arm {idx+1} Size", value=arm.n_allocated or 0)

        # Tab N: Outcomes (if any)
        if "Outcomes" in " ".join(tab_list):
            outcomes_tab = tabs[tab_list.index("Outcomes")]
            with outcomes_tab:
                # DYNAMIC: Render all primary outcomes
                st.subheader("Primary Outcomes")
                for idx, outcome in enumerate(trial_data.primary_outcomes):
                    st.text_input(f"Primary {idx+1}: Name", value=outcome.name)
                    st.text_input(f"Primary {idx+1}: Estimate", value=str(outcome.estimate or ""))

                # DYNAMIC: Render all secondary outcomes
                st.subheader("Secondary Outcomes")
                for idx, outcome in enumerate(trial_data.secondary_outcomes):
                    st.text_input(f"Secondary {idx+1}: Name", value=outcome.name)

        # Tab N: Safety (if any)
        if "Safety" in " ".join(tab_list):
            safety_tab = tabs[tab_list.index("Safety")]
            with safety_tab:
                # DYNAMIC: Render all safety events
                st.subheader("Adverse Events")
                for idx, event in enumerate(trial_data.safety_events):
                    st.text_input(f"Event {idx+1}: Name", value=event.event_name)
                    st.checkbox(f"Event {idx+1}: Serious", value=event.serious)

        return trial_data
```

---

## Testing Strategy

### Test Cases by Trial Type

**Test 1: Cardiovascular RCT (Semaglutide - existing)**
- Same as Phase 1 (verify backward compatibility)
- Parallel, 2 arms, 1 primary outcome
- Expected: Works perfectly (Phase 1 still works)

**Test 2: Oncology RCT (new)**
- Parallel, 2 arms, multiple outcomes
- Primary: Overall Survival (HR)
- Secondary: Progression-Free Survival (HR), Response Rate (%)
- Safety: Multiple event types
- Expected: Extracts all outcomes, scales form

**Test 3: Psychiatric Study (new)**
- Parallel, 3 arms
- Primary: PANSS score change (mean difference)
- Safety: Metabolic, neurological events
- Expected: Handles 3 arms, mean difference outcomes

**Test 4: Pharmacokinetic Study (new)**
- Crossover design
- Primary: AUC (continuous), Cmax (continuous)
- No safety outcomes
- Expected: Detects crossover, handles continuous outcomes

**Test 5: Observational Study (new)**
- Case-control
- Multiple secondary outcomes
- Limited safety data
- Expected: Flexible extraction adapts

---

## Success Criteria

- [x] Flexible schemas design complete (dataclasses)
- [ ] Trial classifier agent working
- [ ] Extraction agent refactored for flexibility
- [ ] Editable form scales dynamically
- [ ] Backward compatible with Phase 1
- [ ] Works on Semaglutide trial (Phase 1)
- [ ] Works on oncology trial (new)
- [ ] Works on psychiatric trial (new)
- [ ] Works on pharmacokinetic trial (new)
- [ ] All tests passing
- [ ] No breaking changes
- [ ] Documentation updated

---

## Files Modified/Created

### New Files
- `schemas/trial_schemas.py` — Type-safe trial structures
- `agents/trial_classifier.py` — Trial type detection
- `utils/schema_mapper.py` — Mapping extraction → dataclass

### Modified Files
- `agents/extraction_agent.py` — Add classifier step, flexible extraction
- `ui/editable_abstract.py` — Dynamic form generation
- `app.py` — Update to use trial_classifier

### Backward Compatibility
- Phase 1 still works
- Semaglutide trial still extracts perfectly
- Editable form still works (just adapts)

---

## Potential Blockers

1. **LLM Hallucination in Outcome Extraction**
   - Mitigation: Add validation chains in Phase 4
   - For now: Users can edit/correct in Phase 1 form

2. **Complex Trial Designs**
   - Mitigation: Start with common designs, expand gradually
   - Fallback: Users can manually specify in form

3. **Different Outcome Naming Conventions**
   - Mitigation: Flexible matching, ask Claude to normalize
   - Fallback: Manual correction in form

---

## Next Steps After Phase 2

Once flexible extraction works:
- Users can upload ANY trial type
- Form adapts to trial complexity
- Better data quality (flexible extraction less error-prone)

Then proceed to Phase 3 (adaptive template) and Phase 4 (hallucination detection).

---

## Time Estimates

- Design schemas: 1 hour ✓ (Pre-planned)
- Trial classifier: 2-3 hours (LLM prompting, testing)
- Extraction refactor: 2-3 hours (Modify prompts, add flexible extraction)
- Schema mapper: 1-2 hours (Dataclass conversion)
- Form updates: 1-2 hours (Dynamic rendering)
- Testing: 2-3 hours (Multiple trial types)
- Documentation: 1 hour

**Total: 10-14 hours** (slightly higher estimate for testing diverse trials)

