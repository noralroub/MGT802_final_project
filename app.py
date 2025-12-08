import streamlit as st
import sys
import os
import tempfile
import json
import logging
from pathlib import Path

try:
    import config
    from core.qa import QASystem
    from core.visual_abstract import VisualAbstractGenerator
    from agents.extraction_agent import EvidenceExtractorAgent
    from utils.visual_abstract_html import (
        VisualAbstractContent,
        render_visual_abstract,
        render_editable_abstract,
        safe_get
    )
    # Ensure config loads properly
    _ = config.OPENAI_API_KEY
except Exception as e:
    st.error(f"Configuration error: {e}")
    st.info("Please ensure all required environment variables are set.")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Medical Visual Abstract Generator", layout="wide")

st.title("🏥 Medical Visual Abstract Generator")
st.markdown("---")

# Sidebar configuration
st.sidebar.title("Settings")
model_choice = st.sidebar.radio(
    "Select LLM Model:",
    options=["gpt-3.5-turbo", "gpt-4"],
    help="Choose between GPT-3.5 Turbo (faster, cheaper) or GPT-4 (more powerful)"
)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📄 Upload & Extract", "❓ Q&A System", "🎨 Visual Abstract"])

with tab1:
    st.header("Upload Medical Paper")
    st.write("Upload a PDF containing your clinical trial data for analysis.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Select a cardiovascular trial paper in PDF format"
    )

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_pdf_path = tmp_file.name

        st.success(f"File uploaded: {uploaded_file.name}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("File Information")
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")

        with col2:
            st.subheader("Processing Options")
            if st.button("🔄 Extract & Analyze Paper", key="extract_btn"):
                with st.spinner("Processing PDF... This may take a minute."):
                    try:
                        # Initialize QA system and ingest PDF
                        qa_system = QASystem(pdf_path=temp_pdf_path, model=model_choice)
                        # Run full evidence extraction for structured outputs
                        extractor = EvidenceExtractorAgent(model=model_choice)
                        extraction_result = extractor.run_full_extraction(temp_pdf_path)

                        st.success("✅ PDF processed and analyzed successfully!")

                        # Store in session state for next tabs
                        st.session_state.qa_system = qa_system
                        st.session_state.pdf_processed = True
                        st.session_state.pdf_name = uploaded_file.name
                        st.session_state.extraction_result = extraction_result

                        st.info("📌 You can now use the Q&A system or generate a visual abstract in the other tabs.")
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        logger.error(f"PDF processing error: {str(e)}")

with tab2:
    st.header("Question & Answer System")
    st.write("Ask questions about the uploaded paper to extract key information.")

    if "pdf_processed" not in st.session_state or not st.session_state.pdf_processed:
        st.warning("⚠️ Please upload and process a PDF first using the 'Upload & Extract' tab.")
    else:
        st.success(f"✅ Paper loaded: {st.session_state.pdf_name}")

        # Sample questions for cardiovascular trials
        st.subheader("Common Questions")
        sample_questions = [
            "What is the primary objective of this trial?",
            "What are the inclusion and exclusion criteria?",
            "What are the main results and primary endpoints?",
            "What is the conclusion of the study?",
            "How many patients were enrolled in the trial?",
            "What was the study duration?",
            "What adverse events were reported?"
        ]

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_question = st.selectbox("Select a predefined question:", sample_questions)
        with col2:
            st.write("")  # Spacing
            if st.button("Ask Selected Question"):
                custom_question = selected_question
                should_ask = True
            else:
                should_ask = False

        st.subheader("Or Ask Your Own Question")
        custom_question = st.text_input("Enter your question about the paper:")

        if custom_question and st.button("Ask Custom Question"):
            should_ask = True
        else:
            should_ask = False

        if should_ask and custom_question:
            with st.spinner("Generating answer..."):
                try:
                    qa_system = st.session_state.qa_system
                    result = qa_system.generate_answer(custom_question)
                    answer = result['answer']

                    st.success("Answer Generated:")
                    st.write(answer)

                    st.caption(f"📊 Sources: {result['num_sources']} | Model: {result['model']}")

                    # Save to session state for visual abstract
                    if "qa_results" not in st.session_state:
                        st.session_state.qa_results = {}
                    st.session_state.qa_results[custom_question] = answer

                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
                    logger.error(f"QA error: {str(e)}")

with tab3:
    st.header("Generate Visual Abstract")
    st.write("Create a professional, publication-ready visual abstract.")

    if "pdf_processed" not in st.session_state or not st.session_state.pdf_processed:
        st.warning("⚠️ Please upload and process a PDF first using the 'Upload & Extract' tab.")
    elif "extraction_result" not in st.session_state:
        st.info("ℹ️ The PDF was not analyzed yet. Please re-run extraction in the first tab.")
    else:
        extraction = st.session_state.get("extraction_result", {})
        structured = extraction.get("structured_abstract", {})
        visual_data = extraction.get("visual_data", {})

        st.success(f"✅ Paper loaded: {st.session_state.pdf_name}")

        # Map extraction data to VisualAbstractContent
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

        # Create editable abstract in sidebar
        edited_content = render_editable_abstract(abstract_content)

        st.divider()

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("Professional Visual Abstract")

        with col2:
            # Export options
            if st.button("📥 Download PNG"):
                try:
                    from utils.visual_abstract_html import build_visual_abstract_html
                    html_content = build_visual_abstract_html(edited_content)
                    # Note: PNG export requires Playwright/Selenium (see optional export feature)
                    st.info("💡 Full PNG export requires additional setup. HTML preview shown above.")
                except Exception as e:
                    st.error(f"Export error: {str(e)}")

        # Render the HTML visual abstract
        render_visual_abstract(edited_content, height=900)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    Medical Visual Abstract Generator for Cardiovascular Trials<br>
    Powered by GPT-3.5/GPT-4 and Streamlit
</div>
""", unsafe_allow_html=True)
