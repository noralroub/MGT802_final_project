import streamlit as st
import sys

try:
    import config
    # Ensure config loads properly
    _ = config.OPENAI_API_KEY
except Exception as e:
    st.error(f"Configuration error: {e}")
    st.info("Please ensure all required environment variables are set.")
    sys.exit(1)

st.set_page_config(page_title="Medical Abstract Generator", layout="wide")

st.title("🏥 Medical Visual Abstract Generator")
st.markdown("---")

st.write("## Hello World!")
st.write("Welcome to the Medical Visual Abstract Generator for Cardiovascular Trials.")
