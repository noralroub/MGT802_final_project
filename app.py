import streamlit as st
import sys
import os
import tempfile
import json
import logging
from pathlib import Path

from ui.visual_template import render_visual_abstract_from_trial

try:
    import config
    from core.qa import QASystem
    from agents.extraction_agent import EvidenceExtractorAgent
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
            ask_selected = st.button("Ask Selected Question")

        st.subheader("Or Ask Your Own Question")
        custom_question = st.text_input("Enter your question about the paper:")

        ask_custom = custom_question and st.button("Ask Custom Question")

        question_to_ask = None
        if ask_custom and custom_question:
            question_to_ask = custom_question
        elif ask_selected:
            question_to_ask = selected_question

        if question_to_ask:
            with st.spinner("Generating answer..."):
                try:
                    qa_system = st.session_state.qa_system
                    result = qa_system.generate_answer(question_to_ask)
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
    st.write("Create an infographic-style summary of the clinical trial data.")

    if "pdf_processed" not in st.session_state or not st.session_state.pdf_processed:
        st.warning("⚠️ Please upload and process a PDF first using the 'Upload & Extract' tab.")
    elif "extraction_result" not in st.session_state:
        st.info("ℹ️ The PDF was not analyzed yet. Please re-run extraction in the first tab.")
    else:
        extraction = st.session_state.get("extraction_result", {})
        structured = extraction.get("structured_abstract", {})
        visual_data = extraction.get("visual_data", {})

        st.success(f"✅ Paper loaded: {st.session_state.pdf_name}")

        with st.expander("View Structured Abstract", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Background")
                st.write(structured.get("background", ""))
                st.subheader("Methods")
                st.write(structured.get("methods", ""))
            with col_b:
                st.subheader("Results")
                st.write(structured.get("results", ""))
                st.subheader("Conclusions")
                st.write(structured.get("conclusions", ""))

        st.divider()

        st.subheader("Visual Abstract Preview")
        if not visual_data:
            st.info("Structured visual data not available yet.")
        elif st.button("🎨 Render Visual Abstract", key="visual_abstract_btn"):
            with st.spinner("Rendering template..."):
                try:
                    render_visual_abstract_from_trial(visual_data, height=820)
                    st.success("✅ Visual abstract rendered below.")
                except Exception as e:
                    st.error(f"Error rendering visual abstract: {str(e)}")
                    logger.error(f"Visual abstract generation error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    Medical Visual Abstract Generator for Cardiovascular Trials<br>
    Powered by GPT-3.5/GPT-4 and Streamlit
</div>
""", unsafe_allow_html=True)
