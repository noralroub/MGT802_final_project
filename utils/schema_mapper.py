"""
Schema Mapper

Converts LLM-extracted JSON data into type-safe ClinicalTrial dataclass instances.

This utility bridges the gap between unstructured LLM output and the flexible
trial data schemas defined in schemas/trial_schemas.py.

Phase 2 Enhancement: Maps generic extracted data to ClinicalTrial objects
that support any study type with any number of outcomes, arms, and safety events.
"""

import logging
from typing import Dict, Any, List, Optional
from schemas.trial_schemas import (
    ClinicalTrial,
    Outcome,
    OutcomeType,
    ArmAllocation,
    SafetyEvent,
    Dosing,
    ConfidenceInterval,
    TrialDesignType,
)

logger = logging.getLogger(__name__)


class SchemaMapper:
    """Maps extracted LLM data to typed ClinicalTrial objects."""

    @staticmethod
    def map_outcome(outcome_data: Dict[str, Any], is_primary: bool = False) -> Outcome:
        """
        Map outcome dictionary to Outcome object.

        Args:
            outcome_data: Dictionary with outcome information
            is_primary: Whether this is a primary outcome

        Returns:
            Outcome object
        """
        measure_type_str = outcome_data.get("measure_type", "unknown")
        try:
            measure_type = OutcomeType(measure_type_str)
        except ValueError:
            logger.warning(f"Unknown measure type: {measure_type_str}, using UNKNOWN")
            measure_type = OutcomeType.UNKNOWN

        ci_data = outcome_data.get("confidence_interval")
        confidence_interval = None
        if ci_data:
            confidence_interval = ConfidenceInterval(
                lower=ci_data.get("lower"),
                upper=ci_data.get("upper"),
                level=ci_data.get("level", 0.95),
            )

        return Outcome(
            name=outcome_data.get("name", "Unknown"),
            measure_type=measure_type,
            estimate=outcome_data.get("estimate"),
            confidence_interval=confidence_interval,
            p_value=outcome_data.get("p_value"),
            units=outcome_data.get("units"),
            definition=outcome_data.get("definition"),
            is_primary=is_primary,
        )

    @staticmethod
    def map_arm(arm_data: Dict[str, Any]) -> ArmAllocation:
        """
        Map arm dictionary to ArmAllocation object.

        Args:
            arm_data: Dictionary with arm information

        Returns:
            ArmAllocation object
        """
        return ArmAllocation(
            label=arm_data.get("label", "Unknown"),
            n_allocated=arm_data.get("n_allocated"),
            n_analyzed=arm_data.get("n_analyzed"),
            n_completed=arm_data.get("n_completed"),
            description=arm_data.get("description"),
        )

    @staticmethod
    def map_safety_event(event_data: Dict[str, Any]) -> SafetyEvent:
        """
        Map safety event dictionary to SafetyEvent object.

        Args:
            event_data: Dictionary with safety event information

        Returns:
            SafetyEvent object
        """
        arm_events = {}
        for arm_label, arm_data in event_data.get("arm_data", {}).items():
            arm_events[arm_label] = {
                "percent": arm_data.get("percent"),
                "count": arm_data.get("count"),
            }

        return SafetyEvent(
            event_name=event_data.get("event_name", "Unknown"),
            event_type=event_data.get("event_type"),
            arm_events=arm_events,
            serious=event_data.get("serious", False),
            led_to_discontinuation=event_data.get("led_to_discontinuation", False),
            notes=event_data.get("notes"),
        )

    @staticmethod
    def map_dosing(dosing_data: Dict[str, Any]) -> Dosing:
        """
        Map dosing dictionary to Dosing object.

        Args:
            dosing_data: Dictionary with dosing information

        Returns:
            Dosing object
        """
        return Dosing(
            description=dosing_data.get("description", ""),
            dose=dosing_data.get("dose"),
            frequency=dosing_data.get("frequency"),
            duration=dosing_data.get("duration"),
            route=dosing_data.get("route"),
            adjustments=dosing_data.get("adjustments"),
        )

    @staticmethod
    def extract_from_picot(picot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract useful fields from PICOT extraction.

        Args:
            picot_data: Output from extract_picot()

        Returns:
            Dictionary with trial info extracted from PICOT
        """
        population = picot_data.get("population", {})
        intervention = picot_data.get("intervention", {})
        timeline = picot_data.get("timeline", {})
        sample_size = picot_data.get("sample_size", {})

        return {
            "inclusion_criteria": population.get("description", ""),
            "inclusion_list": population.get("inclusion", []),
            "exclusion_list": population.get("exclusion", []),
            "intervention_description": intervention.get("description", ""),
            "follow_up_period": timeline.get("follow_up"),
            "duration": timeline.get("duration"),
            "total_enrolled": sample_size.get("total"),
        }

    @staticmethod
    def create_clinical_trial(
        title: str,
        drug_or_intervention: str,
        disease_or_condition: str,
        outcomes_data: Optional[Dict[str, Any]] = None,
        arms_data: Optional[Dict[str, Any]] = None,
        safety_data: Optional[Dict[str, Any]] = None,
        study_classification: Optional[Dict[str, Any]] = None,
        picot_data: Optional[Dict[str, Any]] = None,
        trial_name: Optional[str] = None,
        publication: Optional[str] = None,
        dosing_data: Optional[Dict[str, Any]] = None,
        conclusions: Optional[List[str]] = None,
    ) -> ClinicalTrial:
        """
        Create a ClinicalTrial object from extracted components.

        Args:
            title: Trial title
            drug_or_intervention: Drug/intervention name
            disease_or_condition: Disease/condition being treated
            outcomes_data: Output from extract_outcomes_flexible()
            arms_data: Output from extract_arms_flexible()
            safety_data: Output from extract_safety_events_flexible()
            study_classification: Output from classify_study()
            picot_data: Output from extract_picot()
            trial_name: Trial name/identifier
            publication: Publication reference
            dosing_data: Dosing information
            conclusions: Trial conclusions

        Returns:
            ClinicalTrial object
        """
        trial = ClinicalTrial(
            title=title,
            drug_or_intervention=drug_or_intervention,
            disease_or_condition=disease_or_condition,
            trial_name=trial_name,
            publication=publication,
            conclusions=conclusions or [],
        )

        # Set design from classification if available
        if study_classification:
            design_str = study_classification.get("design", "unknown")
            try:
                trial.design = TrialDesignType(design_str)
            except ValueError:
                logger.warning(f"Unknown design: {design_str}")
                trial.design = TrialDesignType.UNKNOWN

            trial.duration = study_classification.get("follow_up_duration")
            trial.follow_up_period = study_classification.get("follow_up_duration")

        # Extract and set metadata from PICOT if available
        if picot_data:
            picot_info = SchemaMapper.extract_from_picot(picot_data)
            trial.inclusion_criteria = picot_info.get("inclusion_criteria")
            trial.exclusion_criteria = " | ".join(picot_info.get("exclusion_list", []))
            if not trial.duration:
                trial.duration = picot_info.get("duration")
            if not trial.follow_up_period:
                trial.follow_up_period = picot_info.get("follow_up_period")
            if not trial.total_enrolled:
                trial.total_enrolled = picot_info.get("total_enrolled")

        # Add arms
        if arms_data:
            for arm in arms_data.get("arms", []):
                trial.arms.append(SchemaMapper.map_arm(arm))

        # Add outcomes (split into primary/secondary based on flag)
        if outcomes_data:
            for outcome in outcomes_data.get("outcomes", []):
                mapped = SchemaMapper.map_outcome(outcome, is_primary=outcome.get("is_primary", False))
                if mapped.is_primary:
                    trial.primary_outcomes.append(mapped)
                else:
                    trial.secondary_outcomes.append(mapped)

        # Add safety events
        if safety_data:
            for event in safety_data.get("safety_events", []):
                trial.safety_events.append(SchemaMapper.map_safety_event(event))

        # Add dosing if available
        if dosing_data:
            trial.dosing = SchemaMapper.map_dosing(dosing_data)

        return trial

    @staticmethod
    def from_extraction_output(extraction_result: Dict[str, Any]) -> ClinicalTrial:
        """
        Create ClinicalTrial from full extraction output.

        This is the main entry point for converting run_full_extraction() output
        into a typed ClinicalTrial object.

        Args:
            extraction_result: Output from EvidenceExtractorAgent.run_full_extraction()

        Returns:
            ClinicalTrial object
        """
        # Extract title from visual_data if available
        visual_data = extraction_result.get("visual_data", {})
        trial_info = visual_data.get("trial_info", {})

        title = trial_info.get("title", "Unknown Trial")
        drug = trial_info.get("drug", "")
        indication = trial_info.get("indication", "")
        trial_name = trial_info.get("trial_name")
        publication = trial_info.get("publication")

        return SchemaMapper.create_clinical_trial(
            title=title,
            drug_or_intervention=drug,
            disease_or_condition=indication,
            outcomes_data=extraction_result.get("outcomes"),
            arms_data=extraction_result.get("arms"),
            safety_data=extraction_result.get("safety_events"),
            study_classification=extraction_result.get("study_classification"),
            picot_data=extraction_result.get("picot"),
            trial_name=trial_name,
            publication=publication,
            conclusions=visual_data.get("conclusions", []),
        )
