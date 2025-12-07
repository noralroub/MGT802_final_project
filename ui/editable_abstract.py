"""
Editable Visual Abstract UI Component
Allows users to edit trial data and see live preview updates
"""

import streamlit as st
from typing import Dict, Any, List
from ui.visual_template import render_visual_abstract_from_trial


class EditableAbstractForm:
    """Manages editable form fields for visual abstract data."""

    @staticmethod
    def initialize_session_state(initial_data: Dict[str, Any]) -> None:
        """Initialize session state with trial data."""
        if "editable_trial_data" not in st.session_state:
            st.session_state.editable_trial_data = initial_data.copy()
        if "auto_extracted_data" not in st.session_state:
            st.session_state.auto_extracted_data = initial_data.copy()

    @staticmethod
    def render_edit_form(trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render editable form fields and return updated trial data.

        Parameters:
        -----------
        trial_data : Dict[str, Any]
            Initial trial data from extraction

        Returns:
        --------
        Dict[str, Any]
            Updated trial data with user edits
        """
        # Initialize session state
        EditableAbstractForm.initialize_session_state(trial_data)

        st.subheader("✏️ Edit Abstract Fields")
        st.write("Modify any field below to update the visual abstract. Changes will reflect in the preview.")

        # Use tabs to organize form sections
        tab1, tab2, tab3, tab4 = st.tabs(["Trial Info", "Population", "Outcomes", "Results & Safety"])

        # Tab 1: Trial Information
        with tab1:
            st.markdown("**Trial Information**")
            col1, col2 = st.columns(2)

            with col1:
                trial_info = st.session_state.editable_trial_data.get("trial_info", {})
                st.session_state.editable_trial_data["trial_info"] = {
                    "title": st.text_input(
                        "Study Title",
                        value=trial_info.get("title", ""),
                        help="Full title of the clinical trial"
                    ),
                    "drug": st.text_input(
                        "Drug/Intervention",
                        value=trial_info.get("drug", ""),
                        help="Name of the drug or intervention tested"
                    ),
                    "trial_name": st.text_input(
                        "Trial Name/Acronym",
                        value=trial_info.get("trial_name", ""),
                        help="Trial acronym (e.g., SELECT, LEADER)"
                    ),
                }

            with col2:
                st.session_state.editable_trial_data["trial_info"].update({
                    "indication": st.text_input(
                        "Indication",
                        value=trial_info.get("indication", ""),
                        help="Disease or condition being treated"
                    ),
                    "publication": st.text_input(
                        "Publication",
                        value=trial_info.get("publication", ""),
                        help="Journal and year (e.g., NEJM 2023)"
                    ),
                })

        # Tab 2: Population
        with tab2:
            st.markdown("**Study Population**")
            col1, col2 = st.columns(2)

            population = st.session_state.editable_trial_data.get("population", {})

            with col1:
                st.session_state.editable_trial_data["population"] = {
                    "total_enrolled": st.number_input(
                        "Total Enrolled",
                        value=int(population.get("total_enrolled") or 0),
                        min_value=0,
                        help="Total number of participants"
                    ),
                    "arm_1_label": st.text_input(
                        "Arm 1 Label",
                        value=population.get("arm_1_label", ""),
                        help="Name of first treatment arm"
                    ),
                    "arm_1_size": st.number_input(
                        "Arm 1 Size",
                        value=int(population.get("arm_1_size") or 0),
                        min_value=0,
                        help="Number of participants in arm 1"
                    ),
                }

            with col2:
                st.session_state.editable_trial_data["population"].update({
                    "arm_2_label": st.text_input(
                        "Arm 2 Label",
                        value=population.get("arm_2_label", ""),
                        help="Name of second treatment arm"
                    ),
                    "arm_2_size": st.number_input(
                        "Arm 2 Size",
                        value=int(population.get("arm_2_size") or 0),
                        min_value=0,
                        help="Number of participants in arm 2"
                    ),
                    "age_mean": st.number_input(
                        "Mean Age",
                        value=float(population.get("age_mean") or 0),
                        min_value=0.0,
                        format="%.1f",
                        help="Mean age of participants"
                    ),
                })

        # Tab 3: Primary Outcome
        with tab3:
            st.markdown("**Primary Outcome**")
            primary = st.session_state.editable_trial_data.get("primary_outcome", {})

            st.session_state.editable_trial_data["primary_outcome"] = {
                "label": st.text_input(
                    "Outcome Label",
                    value=primary.get("label", ""),
                    help="Name/description of the primary outcome"
                ),
                "effect_measure": st.text_input(
                    "Effect Measure",
                    value=primary.get("effect_measure", ""),
                    help="Type of effect measure (e.g., Hazard Ratio, Odds Ratio)"
                ),
                "estimate": st.text_input(
                    "Estimate",
                    value=primary.get("estimate", ""),
                    help="Numerical estimate/effect size"
                ),
                "ci": st.text_input(
                    "Confidence Interval (95%)",
                    value=primary.get("ci", ""),
                    help="CI format: (lower-upper)"
                ),
                "p_value": st.text_input(
                    "P-value",
                    value=primary.get("p_value", ""),
                    help="Statistical significance"
                ),
            }

        # Tab 4: Results, Event Rates, and Safety
        with tab4:
            st.markdown("**Event Rates**")
            col1, col2 = st.columns(2)

            events = st.session_state.editable_trial_data.get("event_rates", {})

            with col1:
                arm1_pct = st.number_input(
                    "Arm 1 Event Rate (%)",
                    value=float(events.get("arm_1_percent") or 0),
                    min_value=0.0,
                    max_value=100.0,
                    format="%.1f",
                    help="Percentage of events in arm 1"
                )
                st.session_state.editable_trial_data.setdefault("event_rates", {})["arm_1_percent"] = arm1_pct

            with col2:
                arm2_pct = st.number_input(
                    "Arm 2 Event Rate (%)",
                    value=float(events.get("arm_2_percent") or 0),
                    min_value=0.0,
                    max_value=100.0,
                    format="%.1f",
                    help="Percentage of events in arm 2"
                )
                st.session_state.editable_trial_data.setdefault("event_rates", {})["arm_2_percent"] = arm2_pct

            st.markdown("**Adverse Events**")
            adverse = st.session_state.editable_trial_data.get("adverse_events", {})

            st.session_state.editable_trial_data["adverse_events"] = {
                "summary": st.text_area(
                    "Safety Summary",
                    value=adverse.get("summary", ""),
                    height=60,
                    help="Brief summary of adverse events"
                ),
                "notable": st.text_area(
                    "Notable Adverse Events",
                    value="\n".join(adverse.get("notable", [])) if adverse.get("notable") else "",
                    height=80,
                    help="List adverse events (one per line)"
                ).split("\n") if adverse.get("notable") else [],
            }

            st.markdown("**Dosing**")
            dosing = st.session_state.editable_trial_data.get("dosing", {})
            st.session_state.editable_trial_data["dosing"] = {
                "description": st.text_area(
                    "Dosing/Treatment Description",
                    value=dosing.get("description", ""),
                    height=60,
                    help="Dosing regimen and treatment details"
                ),
            }

            st.markdown("**Conclusions**")
            conclusions = st.session_state.editable_trial_data.get("conclusions", [])
            conclusions_text = st.text_area(
                "Key Conclusions",
                value="\n".join(conclusions) if conclusions else "",
                height=80,
                help="List conclusions (one per line)"
            )
            st.session_state.editable_trial_data["conclusions"] = [
                c.strip() for c in conclusions_text.split("\n") if c.strip()
            ]

        return st.session_state.editable_trial_data

    @staticmethod
    def render_comparison_section(original: Dict[str, Any], edited: Dict[str, Any]) -> None:
        """Render a section showing original vs edited data."""
        with st.expander("📊 Compare Original vs Edited"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original (Auto-extracted)")
                st.write(f"**Trial:** {original.get('trial_info', {}).get('title', 'N/A')}")
                st.write(f"**Total Enrolled:** {original.get('population', {}).get('total_enrolled', 'N/A')}")

            with col2:
                st.subheader("Edited Version")
                st.write(f"**Trial:** {edited.get('trial_info', {}).get('title', 'N/A')}")
                st.write(f"**Total Enrolled:** {edited.get('population', {}).get('total_enrolled', 'N/A')}")

    @staticmethod
    def render_with_preview(trial_data: Dict[str, Any], height: int = 800) -> Dict[str, Any]:
        """
        Render edit form with live preview side-by-side.

        Parameters:
        -----------
        trial_data : Dict[str, Any]
            Initial trial data
        height : int
            Height of preview component

        Returns:
        --------
        Dict[str, Any]
            Updated trial data from user edits
        """
        st.markdown("---")

        # Create two columns: form on left, preview on right
        form_col, preview_col = st.columns([1, 1.2], gap="medium")

        with form_col:
            st.subheader("✏️ Edit Fields")
            edited_data = EditableAbstractForm.render_edit_form(trial_data)

        with preview_col:
            st.subheader("👁️ Live Preview")
            render_visual_abstract_from_trial(edited_data, height=height)

        return edited_data

    @staticmethod
    def render_save_section(trial_data: Dict[str, Any]) -> None:
        """Render save and export options."""
        st.markdown("---")
        st.subheader("💾 Save & Export")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                import json
                json_str = json.dumps(trial_data, indent=2)
                st.code(json_str, language="json")
                st.success("Copy the JSON above!")

        with col2:
            if st.button("💾 Download as JSON", use_container_width=True):
                import json
                json_data = json.dumps(trial_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="abstract_data.json",
                    mime="application/json"
                )

        with col3:
            if st.button("✨ Reset to Original", use_container_width=True):
                if "auto_extracted_data" in st.session_state:
                    st.session_state.editable_trial_data = st.session_state.auto_extracted_data.copy()
                    st.success("Reset to original extracted data!")
                    st.rerun()
