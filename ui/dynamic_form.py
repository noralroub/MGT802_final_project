"""
Dynamic Editable Form for ClinicalTrial Objects

Phase 2 Enhancement: Renders form fields dynamically based on study complexity.

Features:
- Adapts to N outcomes (primary + secondary + exploratory)
- Adapts to N arms (2, 3, 5+ arms)
- Adapts to N safety events
- Dynamically creates tabs/sections based on study classification
- Works with flexible ClinicalTrial dataclass structure

This replaces the fixed-structure EditableAbstractForm with a truly flexible
form that scales to any study type.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from schemas.trial_schemas import ClinicalTrial, OutcomeType, TrialDesignType
from ui.visual_template import render_visual_abstract_from_trial


class DynamicEditableForm:
    """Renders editable form fields dynamically based on study complexity."""

    @staticmethod
    def initialize_session_state(trial: ClinicalTrial) -> None:
        """Initialize session state with ClinicalTrial object."""
        if "editable_trial" not in st.session_state:
            st.session_state.editable_trial = trial
        if "original_trial" not in st.session_state:
            st.session_state.original_trial = trial

    @staticmethod
    def render_trial_info_tab(trial: ClinicalTrial) -> None:
        """Render trial identification fields."""
        st.markdown("**Trial Information**")
        col1, col2 = st.columns(2)

        with col1:
            trial.title = st.text_input(
                "Study Title",
                value=trial.title,
                help="Full title of the clinical trial"
            )
            trial.drug_or_intervention = st.text_input(
                "Drug/Intervention",
                value=trial.drug_or_intervention,
                help="Name of the drug or intervention tested"
            )

        with col2:
            trial.trial_name = st.text_input(
                "Trial Name/Acronym",
                value=trial.trial_name or "",
                help="Trial acronym (e.g., SELECT, LEADER)"
            )
            trial.disease_or_condition = st.text_input(
                "Indication",
                value=trial.disease_or_condition,
                help="Disease or condition being treated"
            )

        trial.publication = st.text_input(
            "Publication",
            value=trial.publication or "",
            help="Journal and year (e.g., NEJM 2023)"
        )

    @staticmethod
    def render_design_tab(trial: ClinicalTrial) -> None:
        """Render trial design fields."""
        st.markdown("**Trial Design**")
        col1, col2 = st.columns(2)

        with col1:
            design_options = [d.value for d in TrialDesignType]
            current_design = trial.design.value if trial.design else "unknown"
            selected_design = st.selectbox(
                "Study Design",
                options=design_options,
                index=design_options.index(current_design) if current_design in design_options else 0,
                help="Type of study (RCT, observational, etc.)"
            )
            trial.design = TrialDesignType(selected_design)

        with col2:
            trial.mean_age = st.number_input(
                "Mean Age",
                value=trial.mean_age or 0.0,
                min_value=0.0,
                format="%.1f",
                help="Mean age of participants"
            )

        col1, col2 = st.columns(2)
        with col1:
            trial.duration = st.text_input(
                "Trial Duration",
                value=trial.duration or "",
                help="e.g., 12 weeks, 2 years"
            )

        with col2:
            trial.follow_up_period = st.text_input(
                "Follow-up Period",
                value=trial.follow_up_period or "",
                help="e.g., 6 months, 2 years"
            )

    @staticmethod
    def render_population_tab(trial: ClinicalTrial) -> None:
        """Render dynamic population/arms section."""
        st.markdown("**Study Population**")

        trial.total_enrolled = st.number_input(
            "Total Enrolled",
            value=trial.total_enrolled or 0,
            min_value=0,
            help="Total number of participants"
        )

        trial.inclusion_criteria = st.text_area(
            "Inclusion Criteria",
            value=trial.inclusion_criteria or "",
            height=60,
            help="Key inclusion criteria"
        )

        trial.exclusion_criteria = st.text_area(
            "Exclusion Criteria",
            value=trial.exclusion_criteria or "",
            height=60,
            help="Key exclusion criteria"
        )

        # Dynamic arms section
        st.markdown("**Treatment Arms**")
        st.write(f"Found {len(trial.arms)} arm(s)")

        # Render each arm
        for i, arm in enumerate(trial.arms):
            with st.expander(f"Arm {i+1}: {arm.label}", expanded=(i == 0)):
                col1, col2, col3 = st.columns(3)

                with col1:
                    arm.label = st.text_input(
                        f"Arm {i+1} Label",
                        value=arm.label,
                        key=f"arm_label_{i}",
                        help="Name of treatment arm"
                    )

                with col2:
                    arm.n_allocated = st.number_input(
                        f"Arm {i+1} Allocated",
                        value=arm.n_allocated or 0,
                        min_value=0,
                        key=f"arm_allocated_{i}",
                        help="Participants allocated to this arm"
                    )

                with col3:
                    arm.n_analyzed = st.number_input(
                        f"Arm {i+1} Analyzed",
                        value=arm.n_analyzed or 0,
                        min_value=0,
                        key=f"arm_analyzed_{i}",
                        help="Participants analyzed"
                    )

                arm.description = st.text_area(
                    f"Arm {i+1} Description",
                    value=arm.description or "",
                    height=40,
                    key=f"arm_desc_{i}",
                    help="Treatment description"
                )

        # Option to add more arms
        if st.button("➕ Add Another Arm", use_container_width=True):
            from schemas.trial_schemas import ArmAllocation
            trial.arms.append(ArmAllocation(label=f"Arm {len(trial.arms)+1}"))
            st.rerun()

    @staticmethod
    def render_outcomes_tab(trial: ClinicalTrial) -> None:
        """Render dynamic outcomes section (primary + secondary + exploratory)."""
        st.markdown("**Primary Outcomes**")
        st.write(f"Found {len(trial.primary_outcomes)} primary outcome(s)")

        for i, outcome in enumerate(trial.primary_outcomes):
            with st.expander(f"Primary Outcome {i+1}: {outcome.name}", expanded=(i == 0)):
                col1, col2 = st.columns(2)

                with col1:
                    outcome.name = st.text_input(
                        f"Primary Outcome {i+1} Name",
                        value=outcome.name,
                        key=f"primary_name_{i}",
                        help="Outcome name/label"
                    )

                with col2:
                    measure_options = [m.value for m in OutcomeType]
                    current_measure = outcome.measure_type.value if outcome.measure_type else "unknown"
                    selected_measure = st.selectbox(
                        f"Primary Outcome {i+1} Measure",
                        options=measure_options,
                        index=measure_options.index(current_measure) if current_measure in measure_options else 0,
                        key=f"primary_measure_{i}",
                        help="Type of effect measure"
                    )
                    outcome.measure_type = OutcomeType(selected_measure)

                col1, col2, col3 = st.columns(3)
                with col1:
                    outcome.estimate = st.number_input(
                        f"Primary Outcome {i+1} Estimate",
                        value=float(outcome.estimate or 0.0),
                        format="%.4f",
                        key=f"primary_estimate_{i}",
                        help="Numeric estimate"
                    )

                with col2:
                    if outcome.confidence_interval:
                        ci_lower = st.number_input(
                            f"Primary Outcome {i+1} CI Lower",
                            value=float(outcome.confidence_interval.lower or 0.0),
                            format="%.4f",
                            key=f"primary_ci_lower_{i}",
                        )
                        ci_upper = st.number_input(
                            f"Primary Outcome {i+1} CI Upper",
                            value=float(outcome.confidence_interval.upper or 0.0),
                            format="%.4f",
                            key=f"primary_ci_upper_{i}",
                        )
                        outcome.confidence_interval.lower = ci_lower
                        outcome.confidence_interval.upper = ci_upper

                with col3:
                    outcome.p_value = st.number_input(
                        f"Primary Outcome {i+1} P-value",
                        value=float(outcome.p_value or 0.0),
                        min_value=0.0,
                        max_value=1.0,
                        format="%.4f",
                        key=f"primary_pvalue_{i}",
                    )

        # Secondary outcomes
        if trial.secondary_outcomes:
            st.markdown("**Secondary Outcomes**")
            st.write(f"Found {len(trial.secondary_outcomes)} secondary outcome(s)")

            for i, outcome in enumerate(trial.secondary_outcomes):
                with st.expander(f"Secondary Outcome {i+1}: {outcome.name}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        outcome.name = st.text_input(
                            f"Secondary Outcome {i+1} Name",
                            value=outcome.name,
                            key=f"secondary_name_{i}",
                        )

                    with col2:
                        measure_options = [m.value for m in OutcomeType]
                        current_measure = outcome.measure_type.value if outcome.measure_type else "unknown"
                        selected_measure = st.selectbox(
                            f"Secondary Outcome {i+1} Measure",
                            options=measure_options,
                            index=measure_options.index(current_measure) if current_measure in measure_options else 0,
                            key=f"secondary_measure_{i}",
                        )
                        outcome.measure_type = OutcomeType(selected_measure)

                    outcome.estimate = st.number_input(
                        f"Secondary Outcome {i+1} Estimate",
                        value=float(outcome.estimate or 0.0),
                        format="%.4f",
                        key=f"secondary_estimate_{i}",
                    )

        # Exploratory outcomes
        if trial.exploratory_outcomes:
            st.markdown("**Exploratory Outcomes**")
            st.write(f"Found {len(trial.exploratory_outcomes)} exploratory outcome(s)")

            for i, outcome in enumerate(trial.exploratory_outcomes):
                with st.expander(f"Exploratory Outcome {i+1}: {outcome.name}"):
                    outcome.name = st.text_input(
                        f"Exploratory Outcome {i+1} Name",
                        value=outcome.name,
                        key=f"exploratory_name_{i}",
                    )
                    outcome.estimate = st.number_input(
                        f"Exploratory Outcome {i+1} Estimate",
                        value=float(outcome.estimate or 0.0),
                        key=f"exploratory_estimate_{i}",
                    )

        if st.button("➕ Add Primary Outcome", use_container_width=True):
            from schemas.trial_schemas import Outcome
            trial.primary_outcomes.append(
                Outcome(name="New Outcome", measure_type=OutcomeType.UNKNOWN, is_primary=True)
            )
            st.rerun()

    @staticmethod
    def render_safety_tab(trial: ClinicalTrial) -> None:
        """Render dynamic safety events section."""
        st.markdown("**Safety & Adverse Events**")
        st.write(f"Found {len(trial.safety_events)} safety event(s)")

        for i, event in enumerate(trial.safety_events):
            with st.expander(f"Safety Event {i+1}: {event.event_name}", expanded=(i == 0)):
                col1, col2 = st.columns(2)

                with col1:
                    event.event_name = st.text_input(
                        f"Event {i+1} Name",
                        value=event.event_name,
                        key=f"event_name_{i}",
                        help="Name of adverse event"
                    )

                with col2:
                    event.event_type = st.text_input(
                        f"Event {i+1} Type",
                        value=event.event_type or "",
                        key=f"event_type_{i}",
                        help="e.g., gastrointestinal, cardiovascular"
                    )

                col1, col2 = st.columns(2)
                with col1:
                    event.serious = st.checkbox(
                        f"Event {i+1} is Serious",
                        value=event.serious,
                        key=f"event_serious_{i}",
                    )

                with col2:
                    event.led_to_discontinuation = st.checkbox(
                        f"Event {i+1} Led to Discontinuation",
                        value=event.led_to_discontinuation,
                        key=f"event_disc_{i}",
                    )

                # Per-arm incidence
                st.write("**Incidence by Arm:**")
                for arm_label in [a.label for a in trial.arms]:
                    if arm_label not in event.arm_events:
                        event.arm_events[arm_label] = {"percent": None, "count": None}

                    col1, col2 = st.columns(2)
                    with col1:
                        pct = event.arm_events[arm_label].get("percent")
                        event.arm_events[arm_label]["percent"] = st.number_input(
                            f"{arm_label} - % ({event.event_name})",
                            value=float(pct) if pct is not None else 0.0,
                            min_value=0.0,
                            max_value=100.0,
                            format="%.1f",
                            key=f"event_{i}_pct_{arm_label}",
                        )

                    with col2:
                        cnt = event.arm_events[arm_label].get("count")
                        event.arm_events[arm_label]["count"] = st.number_input(
                            f"{arm_label} - Count ({event.event_name})",
                            value=int(cnt) if cnt is not None else 0,
                            min_value=0,
                            key=f"event_{i}_cnt_{arm_label}",
                        )

        if st.button("➕ Add Safety Event", use_container_width=True):
            from schemas.trial_schemas import SafetyEvent
            trial.safety_events.append(
                SafetyEvent(event_name="New Event", arm_events={a.label: {} for a in trial.arms})
            )
            st.rerun()

    @staticmethod
    def render_conclusions_tab(trial: ClinicalTrial) -> None:
        """Render conclusions section."""
        st.markdown("**Key Conclusions**")

        conclusions_text = st.text_area(
            "Conclusions",
            value="\n".join(trial.conclusions) if trial.conclusions else "",
            height=100,
            help="List conclusions (one per line)"
        )
        trial.conclusions = [c.strip() for c in conclusions_text.split("\n") if c.strip()]

    @staticmethod
    def render_dynamic_form(trial: ClinicalTrial) -> ClinicalTrial:
        """
        Render fully dynamic form based on trial complexity.

        Returns:
            Modified ClinicalTrial object
        """
        DynamicEditableForm.initialize_session_state(trial)

        st.subheader("✏️ Edit Abstract Fields")
        st.write("Modify any field below to update the visual abstract. Changes will reflect in the preview.")

        # Create tabs dynamically based on what data exists
        tabs = ["Trial Info", "Design", "Population & Arms"]
        if trial.primary_outcomes or trial.secondary_outcomes or trial.exploratory_outcomes:
            tabs.append("Outcomes")
        if trial.safety_events:
            tabs.append("Safety")
        tabs.append("Conclusions")

        tab_objects = st.tabs(tabs)

        tab_index = 0

        # Tab 0: Trial Info
        with tab_objects[tab_index]:
            DynamicEditableForm.render_trial_info_tab(trial)
        tab_index += 1

        # Tab 1: Design
        with tab_objects[tab_index]:
            DynamicEditableForm.render_design_tab(trial)
        tab_index += 1

        # Tab 2: Population
        with tab_objects[tab_index]:
            DynamicEditableForm.render_population_tab(trial)
        tab_index += 1

        # Tab 3: Outcomes (if present)
        if trial.primary_outcomes or trial.secondary_outcomes or trial.exploratory_outcomes:
            with tab_objects[tab_index]:
                DynamicEditableForm.render_outcomes_tab(trial)
            tab_index += 1

        # Tab 4: Safety (if present)
        if trial.safety_events:
            with tab_objects[tab_index]:
                DynamicEditableForm.render_safety_tab(trial)
            tab_index += 1

        # Last Tab: Conclusions
        with tab_objects[tab_index]:
            DynamicEditableForm.render_conclusions_tab(trial)

        return trial

    @staticmethod
    def render_with_preview(trial: ClinicalTrial, height: int = 800) -> ClinicalTrial:
        """
        Render dynamic form with live preview side-by-side.

        Returns:
            Modified ClinicalTrial object
        """
        st.markdown("---")

        form_col, preview_col = st.columns([1, 1.2], gap="medium")

        with form_col:
            st.subheader("✏️ Edit Fields")
            edited_trial = DynamicEditableForm.render_dynamic_form(trial)

        with preview_col:
            st.subheader("👁️ Live Preview")
            # Convert to visual_data format for existing preview renderer
            visual_data = DynamicEditableForm._trial_to_visual_data(edited_trial)
            render_visual_abstract_from_trial(visual_data, height=height)

        return edited_trial

    @staticmethod
    def _trial_to_visual_data(trial: ClinicalTrial) -> Dict[str, Any]:
        """Convert ClinicalTrial to legacy visual_data format for preview renderer."""
        return trial.to_dict()

    @staticmethod
    def render_save_section(trial: ClinicalTrial) -> None:
        """Render save and export options."""
        st.markdown("---")
        st.subheader("💾 Save & Export")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                import json
                json_str = json.dumps(trial.to_dict(), indent=2)
                st.code(json_str, language="json")
                st.success("Copy the JSON above!")

        with col2:
            if st.button("💾 Download as JSON", use_container_width=True):
                import json
                json_data = json.dumps(trial.to_dict(), indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="clinical_trial.json",
                    mime="application/json"
                )

        with col3:
            if st.button("✨ Reset to Original", use_container_width=True):
                st.session_state.editable_trial = st.session_state.original_trial
                st.success("Reset to original extracted data!")
                st.rerun()

    @staticmethod
    def render_comparison_section(original: ClinicalTrial, edited: ClinicalTrial) -> None:
        """Render a section showing original vs edited data."""
        with st.expander("📊 Compare Original vs Edited"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original (Auto-extracted)")
                st.write(f"**Trial:** {original.title}")
                st.write(f"**Arms:** {original.num_arms()}")
                st.write(f"**Primary Outcomes:** {original.num_primary_outcomes()}")
                st.write(f"**Total Enrolled:** {original.total_enrolled}")

            with col2:
                st.subheader("Edited Version")
                st.write(f"**Trial:** {edited.title}")
                st.write(f"**Arms:** {edited.num_arms()}")
                st.write(f"**Primary Outcomes:** {edited.num_primary_outcomes()}")
                st.write(f"**Total Enrolled:** {edited.total_enrolled}")
