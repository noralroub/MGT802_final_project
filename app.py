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
                        st.success("✅ PDF processed successfully!")

                        # Store in session state for next tabs
                        st.session_state.qa_system = qa_system
                        st.session_state.pdf_processed = True
                        st.session_state.pdf_name = uploaded_file.name

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
    st.write("Create an infographic-style summary of the clinical trial data.")

    if "pdf_processed" not in st.session_state or not st.session_state.pdf_processed:
        st.warning("⚠️ Please upload and process a PDF first using the 'Upload & Extract' tab.")
    else:
        st.success(f"✅ Paper loaded: {st.session_state.pdf_name}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Layout Options")
            layout_type = st.selectbox(
                "Select layout style:",
                options=["horizontal_3panel", "vertical_4panel"],
                help="Choose how to arrange the visual abstract"
            )

        with col2:
            st.write("")  # Spacing

        if st.button("🎨 Generate Visual Abstract", key="visual_abstract_btn"):
            with st.spinner("Generating visual abstract... This may take a moment."):
                try:
                    # Create visual abstract generator
                    qa_system = st.session_state.qa_system

                    # Get QA results for the visual abstract
                    questions = [
                        "What is the primary objective?",
                        "What are the main results?",
                        "What is the conclusion?",
                        "How many patients were enrolled?"
                    ]

                    qa_results = {}
                    for q in questions:
                        try:
                            result = qa_system.generate_answer(q)
                            qa_results[q] = result['answer']
                        except:
                            qa_results[q] = "Data not available"

                    # Create temporary QA results file
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                        json.dump(qa_results, f)
                        qa_results_path = f.name

                    # Generate visual abstract
                    generator = VisualAbstractGenerator(
                        qa_results_path=qa_results_path,
                        layout_type=layout_type
                    )
                    generator.generate_abstract()

                    # Get image as bytes
                    image_bytes = generator.export_as_bytes()

                    st.success("✅ Visual abstract generated successfully!")

                    # Display image
                    st.image(image_bytes, use_column_width=True)

                    # Download button
                    st.download_button(
                        label="📥 Download Visual Abstract",
                        data=image_bytes,
                        file_name=f"visual_abstract_{Path(st.session_state.pdf_name).stem}.png",
                        mime="image/png"
                    )

                    # Cleanup temp file
                    try:
                        os.remove(qa_results_path)
                    except:
                        pass

                except Exception as e:
                    st.error(f"Error generating visual abstract: {str(e)}")
                    logger.error(f"Visual abstract generation error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    Medical Visual Abstract Generator for Cardiovascular Trials<br>
    Powered by GPT-3.5/GPT-4 and Streamlit
</div>
""", unsafe_allow_html=True)
