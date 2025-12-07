"""
Flexible Trial Data Schemas

Type-safe, extensible dataclasses for representing clinical trials
of ANY type (RCT, observational, crossover, pharmacokinetic, etc.)

This is the core data model for Phase 2+.
Replaces hardcoded fixed schemas with flexible structures.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class OutcomeType(str, Enum):
    """Types of outcome measures - extensible for new types"""

    # Effect measures for comparative studies
    HAZARD_RATIO = "hazard_ratio"
    ODDS_RATIO = "odds_ratio"
    RELATIVE_RISK = "relative_risk"
    RISK_DIFFERENCE = "risk_difference"

    # Mean comparisons
    MEAN_DIFFERENCE = "mean_difference"
    STANDARDIZED_MEAN_DIFFERENCE = "standardized_mean_difference"

    # Binary outcomes
    EVENT_RATE = "event_rate"
    RESPONSE_RATE = "response_rate"
    PERCENTAGE = "percentage"

    # Continuous outcomes
    CONTINUOUS = "continuous"
    CHANGE_FROM_BASELINE = "change_from_baseline"

    # Pharmacokinetic
    AUC = "auc"  # Area under the curve
    CMAX = "cmax"  # Maximum concentration
    TMAX = "tmax"  # Time to maximum concentration
    HALF_LIFE = "half_life"
    CLEARANCE = "clearance"

    # Survival
    SURVIVAL_RATE = "survival_rate"
    MEDIAN_SURVIVAL = "median_survival"

    # Other
    UNKNOWN = "unknown"


class TrialDesignType(str, Enum):
    """Trial design types - extensible for new designs"""

    # Randomized designs
    RCT = "randomized_controlled_trial"
    PARALLEL = "parallel"
    CROSSOVER = "crossover"
    FACTORIAL = "factorial"
    CLUSTER_RCT = "cluster_randomized_trial"

    # Non-randomized
    OBSERVATIONAL = "observational"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"

    # Special designs
    PHARMACOKINETIC = "pharmacokinetic"
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"
    IND_EXPANSION = "ind_expansion"

    # Default
    UNKNOWN = "unknown"


@dataclass
class ConfidenceInterval:
    """Represents a confidence interval"""

    lower: Optional[float] = None
    upper: Optional[float] = None
    level: float = 0.95  # 95%, 90%, 99%, etc.

    def __str__(self) -> str:
        """Pretty print CI"""
        if self.lower is not None and self.upper is not None:
            return f"({self.lower:.2f}-{self.upper:.2f})"
        return "n/a"

    def __repr__(self) -> str:
        return f"CI[{self.level*100:.0f}%]: {str(self)}"

    def to_dict(self) -> Dict[str, Any]:
        return {"lower": self.lower, "upper": self.upper, "level": self.level}


@dataclass
class Outcome:
    """
    Generic outcome structure.

    Works for ANY outcome type:
    - Hazard Ratio (HR)
    - Odds Ratio (OR)
    - Risk Ratio (RR)
    - Mean Difference
    - Event Rate (%)
    - Continuous measures
    - Pharmacokinetic parameters
    """

    name: str
    measure_type: OutcomeType
    estimate: Optional[float] = None
    confidence_interval: Optional[ConfidenceInterval] = None
    p_value: Optional[float] = None
    units: Optional[str] = None
    definition: Optional[str] = None
    is_primary: bool = False
    source_chunk: Optional[str] = None  # For Phase 4: citation tracking

    def __str__(self) -> str:
        """Pretty print outcome"""
        result = f"{self.name}: {self.estimate or 'n/a'}"
        if self.confidence_interval:
            result += f" {self.confidence_interval}"
        if self.p_value:
            result += f" (p={self.p_value})"
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "measure_type": self.measure_type.value,
            "estimate": self.estimate,
            "ci": self.confidence_interval.to_dict() if self.confidence_interval else None,
            "p_value": self.p_value,
            "units": self.units,
            "definition": self.definition,
            "is_primary": self.is_primary,
        }


@dataclass
class ArmAllocation:
    """Allocation and description of a trial arm"""

    label: str
    n_allocated: Optional[int] = None
    n_analyzed: Optional[int] = None
    n_completed: Optional[int] = None
    description: Optional[str] = None

    def __str__(self) -> str:
        """Pretty print arm"""
        result = self.label
        if self.n_allocated:
            result += f" (N={self.n_allocated:,})"
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "n_allocated": self.n_allocated,
            "n_analyzed": self.n_analyzed,
            "n_completed": self.n_completed,
            "description": self.description,
        }


@dataclass
class EventRate:
    """Event rate for a specific arm"""

    label: str
    percent: Optional[float] = None
    count: Optional[int] = None
    denominator: Optional[int] = None
    description: Optional[str] = None

    def __str__(self) -> str:
        """Pretty print event rate"""
        if self.percent is not None:
            return f"{self.label}: {self.percent:.1f}%"
        if self.count is not None and self.denominator is not None:
            pct = (self.count / self.denominator) * 100
            return f"{self.label}: {self.count}/{self.denominator} ({pct:.1f}%)"
        return f"{self.label}: n/a"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "percent": self.percent,
            "count": self.count,
            "denominator": self.denominator,
            "description": self.description,
        }


@dataclass
class SafetyEvent:
    """
    Flexible adverse event/safety data.

    Can represent any type of adverse event:
    - Gastrointestinal (nausea, vomiting, diarrhea)
    - Cardiovascular (MI, stroke, arrhythmia)
    - Laboratory abnormalities
    - Study discontinuation
    - Serious adverse events
    - etc.
    """

    event_name: str
    event_type: Optional[str] = None  # e.g., "gastrointestinal", "cardiovascular", "serious"
    arm_events: Dict[str, Dict[str, Optional[float]]] = field(
        default_factory=dict
    )  # {arm_label: {"percent": 0.0, "count": 0}}
    serious: bool = False
    led_to_discontinuation: bool = False
    notes: Optional[str] = None
    source_chunk: Optional[str] = None  # For Phase 4: citation tracking

    def __str__(self) -> str:
        """Pretty print safety event"""
        result = self.event_name
        if self.serious:
            result += " (serious)"
        if self.led_to_discontinuation:
            result += " (led to discontinuation)"
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.event_name,
            "type": self.event_type,
            "serious": self.serious,
            "discontinuation": self.led_to_discontinuation,
            "arm_data": self.arm_events,
            "notes": self.notes,
        }


@dataclass
class Dosing:
    """Dosing/treatment/intervention information"""

    description: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = None
    adjustments: Optional[str] = None

    def __str__(self) -> str:
        """Pretty print dosing"""
        parts = [self.dose or "", self.frequency or ""]
        return " ".join(filter(None, parts)) or self.description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "dose": self.dose,
            "frequency": self.frequency,
            "duration": self.duration,
            "route": self.route,
            "adjustments": self.adjustments,
        }


@dataclass
class ClinicalTrial:
    """
    Flexible clinical trial data structure.

    This is the CORE DATA MODEL for Phase 2+.

    Key features:
    - Works with ANY trial type (RCT, observational, crossover, etc.)
    - Flexible outcomes (N primary + N secondary + N exploratory)
    - Flexible arms (2, 3, 5, or more)
    - Flexible safety events (any number)
    - Type-safe (uses Enums for common values)
    - Extensible (can add new fields without breaking code)
    - JSON-serializable (for export/import)

    This replaces the Phase 1 hardcoded fixed schema.
    """

    # === REQUIRED IDENTIFIERS (no defaults) ===
    title: str
    drug_or_intervention: str
    disease_or_condition: str

    # === OPTIONAL IDENTIFIERS ===
    trial_name: Optional[str] = None
    publication: Optional[str] = None

    # === TRIAL DESIGN ===
    design: TrialDesignType = TrialDesignType.UNKNOWN

    # === POPULATION ===
    total_enrolled: Optional[int] = None
    arms: List[ArmAllocation] = field(default_factory=list)
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None

    # === DEMOGRAPHICS ===
    mean_age: Optional[float] = None
    age_range: Optional[str] = None
    gender_distribution: Optional[str] = None  # e.g., "60% female"
    baseline_characteristics: Optional[str] = None

    # === OUTCOMES - FLEXIBLE (N primary + N secondary + N exploratory) ===
    primary_outcomes: List[Outcome] = field(default_factory=list)
    secondary_outcomes: List[Outcome] = field(default_factory=list)
    exploratory_outcomes: List[Outcome] = field(default_factory=list)

    # === SAFETY - FLEXIBLE (any number of events) ===
    safety_events: List[SafetyEvent] = field(default_factory=list)

    # === TREATMENT/INTERVENTION ===
    dosing: Optional[Dosing] = None

    # === RESULTS AND CONCLUSIONS ===
    conclusions: List[str] = field(default_factory=list)

    # === METADATA ===
    duration: Optional[str] = None
    follow_up_period: Optional[str] = None
    registry_number: Optional[str] = None  # e.g., NCT number

    # === HELPER METHODS ===

    def num_primary_outcomes(self) -> int:
        """Get number of primary outcomes"""
        return len(self.primary_outcomes)

    def num_secondary_outcomes(self) -> int:
        """Get number of secondary outcomes"""
        return len(self.secondary_outcomes)

    def num_exploratory_outcomes(self) -> int:
        """Get number of exploratory outcomes"""
        return len(self.exploratory_outcomes)

    def num_arms(self) -> int:
        """Get number of treatment arms"""
        return len(self.arms)

    def num_safety_events(self) -> int:
        """Get number of safety events"""
        return len(self.safety_events)

    def all_outcomes(self) -> List[Outcome]:
        """Get all outcomes in order: primary, secondary, exploratory"""
        return self.primary_outcomes + self.secondary_outcomes + self.exploratory_outcomes

    def __str__(self) -> str:
        """Pretty print trial summary"""
        return f"{self.title} | {self.design.value} | {self.num_arms()} arms | {self.num_primary_outcomes()} primary outcomes"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for JSON export)"""
        return {
            "trial_info": {
                "title": self.title,
                "trial_name": self.trial_name,
                "drug": self.drug_or_intervention,
                "indication": self.disease_or_condition,
                "publication": self.publication,
            },
            "design": {
                "type": self.design.value,
                "duration": self.duration,
                "follow_up": self.follow_up_period,
            },
            "population": {
                "total_enrolled": self.total_enrolled,
                "arms": [arm.to_dict() for arm in self.arms],
                "mean_age": self.mean_age,
                "inclusion": self.inclusion_criteria,
                "exclusion": self.exclusion_criteria,
            },
            "outcomes": {
                "primary": [o.to_dict() for o in self.primary_outcomes],
                "secondary": [o.to_dict() for o in self.secondary_outcomes],
                "exploratory": [o.to_dict() for o in self.exploratory_outcomes],
            },
            "safety": {
                "events": [e.to_dict() for e in self.safety_events],
            },
            "treatment": self.dosing.to_dict() if self.dosing else None,
            "conclusions": self.conclusions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClinicalTrial":
        """Create from dictionary (for JSON import)"""
        trial_info = data.get("trial_info", {})
        design_info = data.get("design", {})
        population = data.get("population", {})
        outcomes_data = data.get("outcomes", {})
        safety_data = data.get("safety", {})
        treatment_data = data.get("treatment", {})

        trial = cls(
            title=trial_info.get("title", "Unknown"),
            trial_name=trial_info.get("trial_name"),
            drug_or_intervention=trial_info.get("drug", ""),
            disease_or_condition=trial_info.get("indication", ""),
            publication=trial_info.get("publication"),
            design=TrialDesignType(design_info.get("type", "unknown")),
            total_enrolled=population.get("total_enrolled"),
            mean_age=population.get("mean_age"),
            duration=design_info.get("duration"),
            follow_up_period=design_info.get("follow_up"),
            conclusions=data.get("conclusions", []),
        )

        # Add arms
        for arm_data in population.get("arms", []):
            trial.arms.append(
                ArmAllocation(
                    label=arm_data.get("label", ""),
                    n_allocated=arm_data.get("n_allocated"),
                    n_analyzed=arm_data.get("n_analyzed"),
                )
            )

        # Add outcomes
        for outcome_data in outcomes_data.get("primary", []):
            trial.primary_outcomes.append(
                Outcome(
                    name=outcome_data.get("name", ""),
                    measure_type=OutcomeType(outcome_data.get("measure_type", "unknown")),
                    estimate=outcome_data.get("estimate"),
                    is_primary=True,
                )
            )

        for outcome_data in outcomes_data.get("secondary", []):
            trial.secondary_outcomes.append(
                Outcome(
                    name=outcome_data.get("name", ""),
                    measure_type=OutcomeType(outcome_data.get("measure_type", "unknown")),
                    estimate=outcome_data.get("estimate"),
                    is_primary=False,
                )
            )

        # Add safety events
        for event_data in safety_data.get("events", []):
            trial.safety_events.append(
                SafetyEvent(
                    event_name=event_data.get("name", ""),
                    event_type=event_data.get("type"),
                    serious=event_data.get("serious", False),
                    led_to_discontinuation=event_data.get("discontinuation", False),
                )
            )

        # Add dosing
        if treatment_data:
            trial.dosing = Dosing(
                description=treatment_data.get("description", ""),
                dose=treatment_data.get("dose"),
                frequency=treatment_data.get("frequency"),
            )

        return trial
