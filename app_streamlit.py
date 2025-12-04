"""Streamlit web app for Medical Visual Abstract Generator."""

import streamlit as st
import tempfile
import os
from pathlib import Path

from core.qa import QASystem
from core.visual_abstract import VisualAbstractGenerator
from config import TEST_PDF_PATH, OPENAI_API_KEY


def initialize_session_state():
    """Initialize session state variables."""
    if 'qa_results' not in st.session_state:
        st.session_state.qa_results = None
    if 'trial_data' not in st.session_state:
        st.session_state.trial_data = None
    if 'abstract_image' not in st.session_state:
        st.session_state.abstract_image = None
    if 'qa_processed' not in st.session_state:
        st.session_state.qa_processed = False


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Medical Visual Abstract Generator", layout="wide")

    initialize_session_state()

    # Header
    st.title("🏥 Medical Visual Abstract Generator")
    st.markdown("Transform clinical trial PDFs into professional infographics using AI")

    # Check API key
    if not OPENAI_API_KEY:
        st.error("❌ OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        return

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Upload & Process", "🎨 Visual Abstract", "📊 Detailed Results"])

    # ============================================================================
    # TAB 1: Upload & Process
    # ============================================================================
    with tab1:
        st.header("Step 1: Upload PDF")

        col1, col2 = st.columns([3, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Choose a clinical trial PDF",
                type="pdf",
                help="Upload a medical trial paper to analyze"
            )

        with col2:
            use_test_file = st.checkbox("Use test file", value=False, help="Use the built-in Semaglutide test file")

        if use_test_file and Path(TEST_PDF_PATH).exists():
            pdf_path = TEST_PDF_PATH
            st.info(f"✓ Using test file: {TEST_PDF_PATH}")
        elif uploaded_file:
            pdf_path = None
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getbuffer())
                pdf_path = tmp.name
            st.success(f"✓ Uploaded: {uploaded_file.name}")
        else:
            pdf_path = None
            st.warning("👆 Please upload a PDF or select the test file")

        # Process button
        if st.button("🚀 Generate Visual Abstract", type="primary", use_container_width=True):
            if pdf_path is None:
                st.error("Please upload a PDF first")
            else:
                with st.spinner("Processing PDF... This may take a minute"):
                    try:
                        # Step 1: Run QA system
                        st.write("📖 Ingesting PDF...")
                        qa = QASystem(pdf_path=pdf_path, model="gpt-3.5-turbo")

                        st.write("❓ Asking questions...")
                        questions = [
                            "What was the primary cardiovascular outcome?",
                            "How many patients were enrolled in the trial?",
                            "What was the main adverse event reported?",
                            "What dose of semaglutide was used?",
                            "What were the inclusion criteria for the trial?",
                            "What was the hazard ratio for the primary outcome?",
                            "What are the results comparing semaglutide to placebo?",
                        ]

                        qa_results = {
                            "model": "gpt-3.5-turbo",
                            "num_questions": len(questions),
                            "results": []
                        }

                        for i, question in enumerate(questions, 1):
                            result = qa.generate_answer(question, top_k=3)
                            qa_results['results'].append({
                                "question": question,
                                "answer": result['answer'],
                                "num_sources": result['num_sources'],
                                "tokens_used": result.get('tokens_used', 0)
                            })
                            st.write(f"  ✓ Q{i}/{len(questions)}: {question[:50]}...")

                        st.session_state.qa_results = qa_results
                        st.session_state.qa_processed = True

                        # Step 2: Generate visual abstract
                        st.write("🎨 Generating visual abstract...")
                        generator = VisualAbstractGenerator()
                        generator.trial_data = generator.extractor.extract_key_metrics(qa_results)
                        abstract_image = generator.generate_abstract()

                        st.session_state.abstract_image = abstract_image
                        st.success("✅ Visual abstract generated successfully!")

                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {str(e)}")
                        st.write("Please try again or contact support")

    # ============================================================================
    # TAB 2: Visual Abstract
    # ============================================================================
    with tab2:
        st.header("Visual Abstract")

        if st.session_state.abstract_image:
            st.image(st.session_state.abstract_image, use_column_width=True)

            # Download buttons
            col1, col2 = st.columns(2)

            with col1:
                # PNG download
                generator = VisualAbstractGenerator()
                generator.trial_data = generator.extractor.extract_key_metrics(st.session_state.qa_results)
                generator.image = st.session_state.abstract_image

                png_bytes = generator.export_as_bytes()
                st.download_button(
                    label="📥 Download as PNG",
                    data=png_bytes,
                    file_name="trial_abstract.png",
                    mime="image/png"
                )

            with col2:
                st.info("💡 Use the PNG for presentations, reports, or sharing")

        else:
            st.info("👆 Generate a visual abstract from Tab 1 to see it here")

    # ============================================================================
    # TAB 3: Detailed Results
    # ============================================================================
    with tab3:
        st.header("Detailed QA Results")

        if st.session_state.qa_results:
            st.markdown(f"**Model:** {st.session_state.qa_results['model']}")
            st.markdown(f"**Questions:** {st.session_state.qa_results['num_questions']}")

            st.divider()

            for i, result in enumerate(st.session_state.qa_results['results'], 1):
                with st.expander(f"Q{i}: {result['question']}", expanded=(i == 1)):
                    st.markdown("**Answer:**")
                    st.write(result['answer'])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sources Used", result['num_sources'])
                    with col2:
                        st.metric("Tokens Used", result['tokens_used'])

            # Download JSON
            st.divider()
            st.markdown("**Export Results:**")

            import json
            json_str = json.dumps(st.session_state.qa_results, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name="qa_results.json",
                mime="application/json"
            )

        else:
            st.info("👆 Process a PDF from Tab 1 to see results here")

    # ============================================================================
    # Footer
    # ============================================================================
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**About**")
        st.markdown("AI-powered visual abstract generation from medical trials")

    with col2:
        st.markdown("**Features**")
        st.markdown("- PDF parsing\n- Semantic search\n- LLM Q&A\n- Infographic generation")

    with col3:
        st.markdown("**Tech Stack**")
        st.markdown("- Streamlit\n- OpenAI GPT-3.5\n- Chroma DB\n- PIL/Pillow")


if __name__ == "__main__":
    main()
