"""
Demo Streamlit App for Visual Abstract Template
Run with: streamlit run app.py
"""

import streamlit as st
from visual_abstract import render_visual_abstract, render_blank_template

st.set_page_config(
    page_title="Visual Abstract Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Visual Abstract Generator")
st.markdown("JACC-style visual abstract template for medical research")

# Sidebar for customization
st.sidebar.header("Customize Your Abstract")

with st.sidebar:
    label = st.text_input("Header Label", "CENTRAL ILLUSTRATION")
    title = st.text_input("Title", "Your Study Title Here")
    
    hero_icon = st.selectbox(
        "Hero Icon",
        ["heart", "brain", "lungs", "pill", "dna", "microscope"]
    )
    
    hero_text = st.text_area(
        "Hero Text (use <highlight> tags for gold text)",
        "Main finding with <highlight>key outcome</highlight> highlighted."
    )
    
    intro_text = st.text_area(
        "Introduction Text",
        "Background paragraph describing study methodology."
    )
    
    section_title = st.text_input("Section Title", "TRIAL DESIGN AND POPULATION")
    
    st.subheader("Statistics")
    stat1_value = st.text_input("Stat 1 Value", "210")
    stat1_label = st.text_input("Stat 1 Label (use <br/> for line breaks)", "patients<br/>with condition")
    stat2_value = st.text_input("Stat 2 Value", "Randomized")
    stat2_label = st.text_input("Stat 2 Label", "to treatment<br/>or placebo")
    
    st.subheader("Results")
    primary_outcome = st.text_input("Primary Outcome Label", "Primary outcome = composite:")
    outcome_detail = st.text_input("Outcome Detail", "MACE definition here")
    
    outcome1 = st.text_input("Outcome Item 1", "First outcome measure")
    outcome2 = st.text_input("Outcome Item 2", "Second outcome measure")
    outcome3 = st.text_input("Outcome Item 3", "Third outcome measure")
    
    st.subheader("Bar Chart")
    chart_title = st.text_input("Chart Title (use <br/> for line breaks)", "% Patients With Outcome")
    
    bar1_label = st.text_input("Bar 1 Label", "Treatment A")
    bar1_value = st.slider("Bar 1 Value", 0, 100, 47)
    bar1_n = st.number_input("Bar 1 N", value=68, min_value=0)
    bar1_color = st.selectbox("Bar 1 Color", ["blue", "red", "gray", "teal", "gold", "navy"], index=0)
    
    bar2_label = st.text_input("Bar 2 Label", "Treatment B")
    bar2_value = st.slider("Bar 2 Value", 0, 100, 59)
    bar2_n = st.number_input("Bar 2 N", value=69, min_value=0)
    bar2_color = st.selectbox("Bar 2 Color", ["blue", "red", "gray", "teal", "gold", "navy"], index=1)
    
    bar3_label = st.text_input("Bar 3 Label", "Placebo")
    bar3_value = st.slider("Bar 3 Value", 0, 100, 53)
    bar3_n = st.number_input("Bar 3 N", value=70, min_value=0)
    bar3_color = st.selectbox("Bar 3 Color", ["blue", "red", "gray", "teal", "gold", "navy"], index=2)
    
    footer = st.text_input("Footer Citation", "Journal Year | Authors | Citation")

# Main content area
st.subheader("Preview")

render_visual_abstract(
    label=label,
    title=title,
    hero_icon=hero_icon,
    hero_text=hero_text,
    intro_text=intro_text,
    section_title=section_title,
    stats=[
        {"value": stat1_value, "label": stat1_label, "icon": "people"},
        {"value": stat2_value, "label": stat2_label, "icon": "randomize"},
    ],
    icon_rows=[
        {"icon": "multicenter", "text": "Multicenter"},
        {"icon": "calendar", "text": "30-day follow-up"},
    ],
    results_title="RESULTS",
    primary_outcome=primary_outcome,
    outcome_detail=outcome_detail,
    outcome_items=[
        {"text": outcome1, "positive": False},
        {"text": outcome2, "positive": False},
        {"text": outcome3, "positive": False},
    ],
    chart_title=chart_title,
    bar_data=[
        {"label": bar1_label, "value": bar1_value, "n": bar1_n, "color": bar1_color},
        {"label": bar2_label, "value": bar2_value, "n": bar2_n, "color": bar2_color},
        {"label": bar3_label, "value": bar3_value, "n": bar3_n, "color": bar3_color},
    ],
    footer=footer,
    height=720
)

# Quick reference section
with st.expander("📖 Quick Start Code & Reference"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Usage Example:**")
        st.code('''
from visual_abstract import render_visual_abstract

render_visual_abstract(
    label="CENTRAL ILLUSTRATION",
    title="Your Study Title",
    hero_icon="heart",
    hero_text="Finding with <highlight>key result</highlight>",
    intro_text="Study background...",
    section_title="METHODS",
    stats=[
        {"value": "100", "label": "patients", "icon": "people"},
        {"value": "RCT", "label": "design", "icon": "randomize"},
    ],
    bar_data=[
        {"label": "A", "value": 45, "n": 50, "color": "blue"},
        {"label": "B", "value": 60, "n": 50, "color": "red"},
    ],
    footer="Citation"
)
        ''', language="python")
    
    with col2:
        st.markdown("**Available Options:**")
        st.markdown("""
        **Hero Icons:** `heart`, `brain`, `lungs`, `pill`, `dna`, `microscope`
        
        **Stat Icons:** `people`, `randomize`, `chart`, `clock`, `checkmark`
        
        **Row Icons:** `multicenter`, `calendar`, `clock`, `chart`, `checkmark`
        
        **Bar Colors:** `blue`, `red`, `gray`, `teal`, `gold`, `navy`
        
        **Tips:**
        - Use `<highlight>text</highlight>` for gold text in hero
        - Use `<br/>` for line breaks in labels
        - Set `positive=True` for green checkmarks (✓) vs red X (✗)
        """)
