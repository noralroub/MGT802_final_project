"""Streamlit web app for Medical Visual Abstract Generator."""

import streamlit as st
import json
import os
from pathlib import Path

from utils.data_extraction import TrialDataExtractor
from ui.visual_template import render_visual_abstract_from_trial


def load_demo_qa_results():
    """Load demo QA results from file."""
    demo_path = Path("data/debug_output/qa_results.json")
    if demo_path.exists():
        with open(demo_path) as f:
            return json.load(f)
    return None


def initialize_session_state():
    """Initialize session state variables."""
    if 'qa_results' not in st.session_state:
        st.session_state.qa_results = None
    if 'abstract_data' not in st.session_state:
        st.session_state.abstract_data = None
    if 'demo_loaded' not in st.session_state:
        st.session_state.demo_loaded = False


def generate_abstract_from_qa(qa_results):
    """Convert QA results into structured trial data."""
    try:
        extractor = TrialDataExtractor()
        if qa_results:
            trial_data = extractor.extract_key_metrics(qa_results)
        else:
            trial_data = extractor.extract_key_metrics(
                extractor.load_qa_results("data/debug_output/qa_results.json")
            )
        return trial_data
    except Exception as e:
        st.error(f"Error preparing abstract: {str(e)}")
        return None


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Medical Visual Abstract Generator",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    initialize_session_state()

    # Header
    st.title("🏥 Medical Visual Abstract Generator")
    st.markdown("Transform clinical trial PDFs into professional infographics")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This app generates professional visual abstracts from clinical trial data.

        **Features:**
        - Display trial infographics
        - Upload QA results JSON

        **Data:** Semaglutide Trial (NEJM 2023)
        """)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Visual Abstract", "📁 Upload Results", "ℹ️ Info"])

    # ============================================================================
    # TAB 1: Visual Abstract Display
    # ============================================================================
    with tab1:
        st.header("Clinical Trial Visual Abstract")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.write("Display and download professional infographics")
        with col2:
            if st.button("🔄 Load Demo", use_container_width=True):
                st.session_state.qa_results = load_demo_qa_results()
                if st.session_state.qa_results:
                    st.session_state.abstract_data = generate_abstract_from_qa(st.session_state.qa_results)
                    st.session_state.demo_loaded = True

        st.divider()

        # Show abstract if loaded
        if st.session_state.abstract_data:
            render_visual_abstract_from_trial(st.session_state.abstract_data, height=820)
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.info("👆 Click 'Load Demo' to view the Semaglutide trial infographic")
            with col2:
                st.info("Or upload QA results JSON in the 'Upload Results' tab")

    # ============================================================================
    # TAB 2: Upload Results
    # ============================================================================
    with tab2:
        st.header("Upload QA Results")

        st.markdown("""
        Upload a JSON file containing QA results to generate a custom visual abstract.

        **Expected JSON format:**
        ```json
        {
            "model": "gpt-3.5-turbo",
            "num_questions": 7,
            "results": [
                {"question": "...", "answer": "..."},
                ...
            ]
        }
        ```
        """)

        st.divider()

        uploaded_file = st.file_uploader(
            "Choose a QA results JSON file",
            type="json",
            help="Upload the qa_results.json file from Sprint 3"
        )

        if uploaded_file:
            try:
                qa_results = json.load(uploaded_file)
                st.session_state.qa_results = qa_results

                st.success("✅ QA results loaded successfully")

                # Show summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model", qa_results.get("model", "Unknown"))
                with col2:
                    st.metric("Questions", qa_results.get("num_questions", 0))
                with col3:
                    st.metric("Results", len(qa_results.get("results", [])))

                st.divider()

                # Generate button
                if st.button("🎨 Render Visual Abstract", type="primary", use_container_width=True):
                    with st.spinner("Preparing infographic..."):
                        st.session_state.abstract_data = generate_abstract_from_qa(qa_results)
                        if st.session_state.abstract_data:
                            st.success("✅ Visual abstract ready! View it in the 'Visual Abstract' tab.")
                        else:
                            st.error("Unable to create abstract from this file.")

            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please check the format.")
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")

    # ============================================================================
    # TAB 3: Information
    # ============================================================================
    with tab3:
        st.header("How It Works")

        st.subheader("1️⃣ Data Extraction")
        st.markdown("""
        The system extracts structured metrics from QA results using regex patterns:
        - Population demographics
        - Primary outcome statistics
        - Adverse events
        - Treatment information
        - Body weight changes
        """)

        st.subheader("2️⃣ Layout Design")
        st.markdown("""
        JACC-style HTML layout rendered directly in Streamlit:
        - Prominent hero banner for key findings
        - Structured left/right columns for population and results
        - Custom icons, stat boxes, and bar chart
        """)

        st.subheader("3️⃣ Visual Generation")
        st.markdown("""
        Templates render as responsive HTML components:
        - Styled via CSS for crisp typography
        - SVG icons for sharp visuals
        - Ideal for quick previews and presentations
        """)

        st.divider()

        st.subheader("📋 QA Results Format")
        st.code("""
{
    "model": "gpt-3.5-turbo",
    "num_questions": 7,
    "results": [
        {
            "question": "What was the primary outcome?",
            "answer": "...",
            "num_sources": 3,
            "tokens_used": 250
        }
    ]
}
        """, language="json")

        st.divider()

        st.subheader("🏥 Example Trial Data")
        example_trial = {
            "Trial": "Semaglutide and Cardiovascular Outcomes in Obesity",
            "Publication": "NEJM 2023",
            "Patients": "17,604 (8,803 drug, 8,801 placebo)",
            "Primary Outcome": "Hazard Ratio: 0.80 (95% CI: 0.72-0.90, P<0.001)",
            "Event Rates": "6.5% vs 8.0%",
            "Body Weight": "Semaglutide -9.39%, Placebo -0.88%",
            "Adverse Events": "GI symptoms 16.6% vs 10.0%"
        }

        for key, value in example_trial.items():
            st.write(f"**{key}:** {value}")

        st.divider()

        st.subheader("📚 Tech Stack")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **Frontend**
            - Streamlit
            - Custom HTML/CSS template
            """)
        with col2:
            st.markdown("""
            **Backend**
            - Python 3.9+
            - OpenAI API
            - Trial data extractor
            """)
        with col3:
            st.markdown("""
            **Data**
            - JSON QA results
            - Regex extraction
            - Structured trial schema
            """)

        st.divider()

        st.markdown("""
        **Created for:** MGT802 Final Project
        **Version:** 1.0 (Sprint 4)
        """)


if __name__ == "__main__":
    main()
