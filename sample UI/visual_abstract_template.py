"""
JACC-Style Visual Abstract Template (Fixed for Streamlit 1.x)
==============================================================

A structured visual abstract template with FIXED layout and FILLABLE content zones.
Uses st.components.v1.html for proper HTML rendering.

Author: Infodemica Team
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any


# =============================================================================
# CONFIGURATION - COLORS & STYLING
# =============================================================================

COLORS = {
    "header_bg": "#1e3a5f",        # Dark navy blue
    "hero_bg": "#c41e3a",          # Crimson red  
    "hero_highlight": "#ffd700",   # Gold for highlighted text
    "methods_banner": "#2d4a6f",   # Darker blue for methods banner
    "results_header": "#c41e3a",   # Crimson for results header
    "box_border": "#e0e0e0",       # Light gray borders
    "text_primary": "#1a1a1a",     # Near black
    "text_secondary": "#4a5568",   # Gray
    "background": "#f8f9fa",       # Light gray background
    "white": "#ffffff",
    "footer_bg": "#2d4a6f",        # Dark blue footer
}


# =============================================================================
# SVG ICONS (Fixed/Constant)
# =============================================================================

def get_heart_icon() -> str:
    """Heart icon for the hero section."""
    return """
    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 88C50 88 10 58 10 35C10 20 22 10 35 10C42 10 48 14 50 18C52 14 58 10 65 10C78 10 90 20 90 35C90 58 50 88 50 88Z" 
              stroke="white" stroke-width="4" fill="rgba(255,255,255,0.2)"/>
        <ellipse cx="32" cy="32" rx="8" ry="10" fill="rgba(255,255,255,0.3)"/>
    </svg>
    """

def get_participants_icon() -> str:
    """Person/participants icon."""
    return """
    <svg viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
        <circle cx="30" cy="18" r="10" fill="#48a9a6"/>
        <ellipse cx="30" cy="48" rx="18" ry="14" fill="#48a9a6"/>
    </svg>
    """

def get_intervention_icon() -> str:
    """Intervention/treatment icon (connected nodes)."""
    return """
    <svg viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
        <circle cx="15" cy="30" r="8" fill="#4a90d9"/>
        <circle cx="45" cy="15" r="6" fill="#e8b44a"/>
        <circle cx="45" cy="45" r="6" fill="#d94a4a"/>
        <line x1="22" y1="27" x2="39" y2="17" stroke="#4a90d9" stroke-width="3"/>
        <line x1="22" y1="33" x2="39" y2="43" stroke="#4a90d9" stroke-width="3"/>
    </svg>
    """

def get_chart_placeholder_icon() -> str:
    """Placeholder icon when no chart data is provided."""
    return """
    <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="45" width="15" height="25" fill="#c41e3a" rx="2"/>
        <rect x="32" y="30" width="15" height="40" fill="#c41e3a" rx="2"/>
        <rect x="54" y="15" width="15" height="55" fill="#c41e3a" rx="2"/>
    </svg>
    """


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def process_highlight(text: str) -> str:
    """Convert <highlight>text</highlight> tags to styled spans."""
    if not text:
        return ""
    return text.replace(
        "<highlight>", '<span class="highlight">'
    ).replace(
        "</highlight>", "</span>"
    )


def render_bar_chart(data: Dict[str, float]) -> str:
    """Render a simple bar chart from data."""
    if not data:
        return f'<div class="va-stat-icon">{get_chart_placeholder_icon()}</div>'
    
    max_val = max(data.values()) if data.values() else 1
    
    bars_html = []
    for label, value in data.items():
        height = int((value / max_val) * 80) + 20
        bars_html.append(f'''
            <div class="va-bar-item">
                <div class="va-bar" style="height: {height}px;">{value}%</div>
                <div class="va-bar-label">{label}</div>
            </div>
        ''')
    
    return f'<div class="va-bar-chart">{"".join(bars_html)}</div>'


def safe_get(data: dict, key: str, default: any = "") -> any:
    """Safely get a value from dict."""
    value = data.get(key)
    return default if value is None else value


# =============================================================================
# MAIN HTML BUILDER
# =============================================================================

def build_visual_abstract_html(content: Dict[str, Any]) -> str:
    """
    Build the complete HTML for the visual abstract.
    
    Args:
        content: Dictionary with all the content fields
        
    Returns:
        Complete HTML string with embedded CSS
    """
    
    # Extract content with defaults
    title = safe_get(content, "title", "Research Paper Title")
    main_finding = process_highlight(safe_get(content, "main_finding", "Main finding goes here."))
    background = safe_get(content, "background", "Background context goes here...")
    methods_summary = safe_get(content, "methods_summary", "Methods/Study Design")
    participants = safe_get(content, "participants", "[###]")
    participants_label = safe_get(content, "participants_label", "Number of participants")
    intervention = safe_get(content, "intervention", "[Label]")
    intervention_label = safe_get(content, "intervention_label", "Intervention type")
    methods_description = safe_get(content, "methods_description", "Methods description goes here...")
    results = safe_get(content, "results", ["Result 1", "Result 2", "Result 3"])
    chart_title = safe_get(content, "chart_title", "Visual Summary")
    chart_subtitle = safe_get(content, "chart_subtitle", "")
    chart_data = safe_get(content, "chart_data", None)
    journal = safe_get(content, "journal", "[Journal Name]")
    year = safe_get(content, "year", "[Year]")
    authors = safe_get(content, "authors", "[Authors]")
    doi = safe_get(content, "doi", "[DOI]")
    
    # Build results list HTML
    results_html = "".join([f"<li>{r}</li>" for r in results if r])
    
    # Build chart content
    if chart_data:
        chart_content = render_bar_chart(chart_data)
    else:
        chart_content = f'''
            <div style="width:80px;height:80px;margin:0 auto;">
                {get_chart_placeholder_icon()}
            </div>
            <div style="font-size:0.8rem;color:#666;margin-top:8px;">
                Chart or relevant visual
            </div>
        '''
    
    # Complete HTML with embedded CSS
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&family=Roboto+Slab:wght@500;700&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Open Sans', sans-serif;
                background: transparent;
            }}
            
            .va-container {{
                max-width: 900px;
                margin: 0 auto;
                background: {COLORS['white']};
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                border-radius: 4px;
                overflow: hidden;
            }}
            
            /* Header */
            .va-header {{
                background: {COLORS['header_bg']};
                padding: 14px 24px;
            }}
            .va-header-title {{
                font-family: 'Roboto Slab', serif;
                font-size: 1.1rem;
                font-weight: 700;
                color: {COLORS['white']};
                margin: 0;
            }}
            
            /* Hero */
            .va-hero {{
                background: {COLORS['hero_bg']};
                padding: 28px 24px;
                display: flex;
                align-items: flex-start;
                gap: 20px;
            }}
            .va-hero-icon {{
                flex-shrink: 0;
                width: 70px;
                height: 70px;
            }}
            .va-hero-icon svg {{
                width: 60px;
                height: 60px;
            }}
            .va-hero-text {{
                flex: 1;
                font-size: 1.1rem;
                line-height: 1.6;
                color: {COLORS['white']};
            }}
            .va-hero-text .highlight {{
                color: {COLORS['hero_highlight']};
                font-weight: 700;
            }}
            
            /* Two-column body */
            .va-body {{
                display: flex;
                background: {COLORS['background']};
                min-height: 380px;
            }}
            .va-left-column {{
                flex: 1;
                padding: 20px;
                border-right: 1px dashed {COLORS['box_border']};
            }}
            .va-right-column {{
                flex: 1;
                padding: 20px;
            }}
            
            /* Content boxes */
            .va-box {{
                background: {COLORS['white']};
                border: 2px solid {COLORS['box_border']};
                border-radius: 4px;
                padding: 16px;
                margin-bottom: 16px;
            }}
            .va-box-content {{
                font-size: 0.9rem;
                line-height: 1.6;
                color: {COLORS['text_primary']};
            }}
            
            /* Methods banner */
            .va-methods-banner {{
                background: {COLORS['methods_banner']};
                color: {COLORS['white']};
                padding: 10px 20px;
                border-radius: 25px;
                text-align: center;
                font-weight: 600;
                font-size: 0.95rem;
                margin-bottom: 20px;
            }}
            
            /* Stats row */
            .va-stats-row {{
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
                padding: 10px 0;
            }}
            .va-stat-item {{
                text-align: center;
            }}
            .va-stat-icon {{
                width: 50px;
                height: 50px;
                margin: 0 auto 8px auto;
            }}
            .va-stat-icon svg {{
                width: 50px;
                height: 50px;
            }}
            .va-stat-number {{
                font-size: 1.3rem;
                font-weight: 700;
                color: {COLORS['text_primary']};
                margin-bottom: 4px;
            }}
            .va-stat-label {{
                font-size: 0.75rem;
                color: {COLORS['text_secondary']};
                line-height: 1.3;
                max-width: 120px;
                margin: 0 auto;
            }}
            
            /* Results box */
            .va-results-box {{
                background: {COLORS['white']};
                border: 2px solid {COLORS['box_border']};
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 16px;
            }}
            .va-results-header {{
                background: {COLORS['results_header']};
                color: {COLORS['white']};
                padding: 10px 16px;
                font-weight: 700;
                font-size: 0.95rem;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            .va-results-content {{
                padding: 16px;
            }}
            .va-results-intro {{
                font-size: 0.85rem;
                color: {COLORS['text_secondary']};
                margin-bottom: 12px;
                text-align: center;
            }}
            .va-results-list {{
                list-style: decimal;
                padding-left: 24px;
                margin: 0;
            }}
            .va-results-list li {{
                font-size: 0.85rem;
                line-height: 1.5;
                color: {COLORS['text_primary']};
                margin-bottom: 6px;
            }}
            
            /* Chart box */
            .va-chart-box {{
                background: {COLORS['white']};
                border: 2px solid {COLORS['box_border']};
                border-radius: 4px;
                padding: 16px;
                text-align: center;
            }}
            .va-chart-title {{
                font-size: 1rem;
                font-weight: 700;
                color: {COLORS['results_header']};
                margin-bottom: 4px;
            }}
            .va-chart-subtitle {{
                font-size: 0.85rem;
                color: {COLORS['text_secondary']};
                margin-bottom: 16px;
            }}
            .va-chart-area {{
                min-height: 120px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            
            /* Bar chart */
            .va-bar-chart {{
                display: flex;
                align-items: flex-end;
                justify-content: center;
                gap: 16px;
                height: 100px;
            }}
            .va-bar-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .va-bar {{
                width: 40px;
                background: {COLORS['hero_bg']};
                border-radius: 4px 4px 0 0;
                display: flex;
                align-items: flex-start;
                justify-content: center;
                padding-top: 4px;
                color: white;
                font-weight: 700;
                font-size: 0.75rem;
            }}
            .va-bar-label {{
                font-size: 0.7rem;
                color: {COLORS['text_secondary']};
                margin-top: 4px;
            }}
            
            /* Footer */
            .va-footer {{
                background: {COLORS['footer_bg']};
                padding: 12px 24px;
                color: {COLORS['white']};
                font-size: 0.8rem;
            }}
            
            /* Responsive */
            @media (max-width: 700px) {{
                .va-body {{
                    flex-direction: column;
                }}
                .va-left-column {{
                    border-right: none;
                    border-bottom: 1px dashed {COLORS['box_border']};
                }}
            }}
        </style>
    </head>
    <body>
        <div class="va-container">
            <!-- HEADER -->
            <div class="va-header">
                <h1 class="va-header-title">{title}</h1>
            </div>
            
            <!-- HERO: Main Finding -->
            <div class="va-hero">
                <div class="va-hero-icon">
                    {get_heart_icon()}
                </div>
                <div class="va-hero-text">
                    {main_finding}
                </div>
            </div>
            
            <!-- TWO-COLUMN BODY -->
            <div class="va-body">
                <!-- LEFT COLUMN -->
                <div class="va-left-column">
                    <!-- Background Box -->
                    <div class="va-box">
                        <div class="va-box-content">{background}</div>
                    </div>
                    
                    <!-- Methods Banner -->
                    <div class="va-methods-banner">{methods_summary}</div>
                    
                    <!-- Stats: Participants & Intervention -->
                    <div class="va-stats-row">
                        <div class="va-stat-item">
                            <div class="va-stat-icon">
                                {get_participants_icon()}
                            </div>
                            <div class="va-stat-number">{participants}</div>
                            <div class="va-stat-label">{participants_label}</div>
                        </div>
                        <div class="va-stat-item">
                            <div class="va-stat-icon">
                                {get_intervention_icon()}
                            </div>
                            <div class="va-stat-number">{intervention}</div>
                            <div class="va-stat-label">{intervention_label}</div>
                        </div>
                    </div>
                    
                    <!-- Methods Description Box -->
                    <div class="va-box">
                        <div class="va-box-content">{methods_description}</div>
                    </div>
                </div>
                
                <!-- RIGHT COLUMN -->
                <div class="va-right-column">
                    <!-- Results Box -->
                    <div class="va-results-box">
                        <div class="va-results-header">Results</div>
                        <div class="va-results-content">
                            <div class="va-results-intro">Key findings:</div>
                            <ol class="va-results-list">
                                {results_html}
                            </ol>
                        </div>
                    </div>
                    
                    <!-- Chart Area -->
                    <div class="va-chart-box">
                        <div class="va-chart-title">{chart_title}</div>
                        <div class="va-chart-subtitle">{chart_subtitle}</div>
                        <div class="va-chart-area">
                            {chart_content}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- FOOTER -->
            <div class="va-footer">
                <div class="va-citation">
                    {journal} {year} | {authors} | {doi}
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render_visual_abstract(content: Dict[str, Any], height: int = 700) -> None:
    """
    Render the visual abstract using st.components.v1.html.
    
    Args:
        content: Dictionary with content fields:
            REQUIRED:
            - title: Paper title
            - main_finding: Key conclusion (use <highlight>text</highlight> for emphasis)
            - background: 2-4 sentences context
            - methods_description: 2-4 sentences methodology
            - results: List of 3-4 bullet points
            
            OPTIONAL:
            - methods_summary: Short label (e.g., "Randomized Controlled Trial")
            - participants: Number (e.g., "10,000")
            - participants_label: Description
            - intervention: Short label
            - intervention_label: Comparison
            - chart_title, chart_subtitle, chart_data
            - journal, year, authors, doi
            
        height: Height of the component in pixels
    """
    html = build_visual_abstract_html(content)
    components.html(html, height=height, scrolling=True)


# =============================================================================
# EDITABLE VERSION
# =============================================================================

def render_editable_abstract(initial_content: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Render an editable version with sidebar controls.
    
    Args:
        initial_content: Pre-filled content from AI agents
        
    Returns:
        Dictionary with edited content
    """
    
    if initial_content is None:
        initial_content = {}
    
    edited = {}
    
    with st.sidebar:
        st.header("✏️ Edit Content")
        
        st.subheader("Header")
        edited["title"] = st.text_input(
            "Title", 
            value=safe_get(initial_content, "title", "Paper Title")
        )
        
        st.subheader("Main Finding")
        edited["main_finding"] = st.text_area(
            "Main Finding",
            value=safe_get(initial_content, "main_finding", ""),
            height=80,
            help="Use <highlight>text</highlight> for gold emphasis"
        )
        
        st.subheader("Background")
        edited["background"] = st.text_area(
            "Background (2-4 sentences)",
            value=safe_get(initial_content, "background", ""),
            height=80
        )
        
        st.subheader("Methods")
        edited["methods_summary"] = st.text_input(
            "Methods Banner",
            value=safe_get(initial_content, "methods_summary", "Methods/Study Design")
        )
        
        col1, col2 = st.columns(2)
        with col1:
            edited["participants"] = st.text_input(
                "Participants #",
                value=safe_get(initial_content, "participants", "")
            )
            edited["participants_label"] = st.text_input(
                "Participants Label",
                value=safe_get(initial_content, "participants_label", "")
            )
        with col2:
            edited["intervention"] = st.text_input(
                "Intervention",
                value=safe_get(initial_content, "intervention", "")
            )
            edited["intervention_label"] = st.text_input(
                "Intervention Label",
                value=safe_get(initial_content, "intervention_label", "")
            )
        
        edited["methods_description"] = st.text_area(
            "Methods Description",
            value=safe_get(initial_content, "methods_description", ""),
            height=80
        )
        
        st.subheader("Results")
        results_default = safe_get(initial_content, "results", [])
        results_text = st.text_area(
            "Results (one per line)",
            value="\n".join(results_default) if isinstance(results_default, list) else "",
            height=100
        )
        edited["results"] = [r.strip() for r in results_text.split("\n") if r.strip()]
        
        st.subheader("Chart")
        edited["chart_title"] = st.text_input(
            "Chart Title",
            value=safe_get(initial_content, "chart_title", "")
        )
        edited["chart_subtitle"] = st.text_input(
            "Chart Subtitle",
            value=safe_get(initial_content, "chart_subtitle", "")
        )
        
        st.subheader("Citation")
        c1, c2 = st.columns(2)
        with c1:
            edited["journal"] = st.text_input(
                "Journal",
                value=safe_get(initial_content, "journal", "")
            )
            edited["year"] = st.text_input(
                "Year",
                value=safe_get(initial_content, "year", "")
            )
        with c2:
            edited["authors"] = st.text_input(
                "Authors",
                value=safe_get(initial_content, "authors", "")
            )
            edited["doi"] = st.text_input(
                "DOI",
                value=safe_get(initial_content, "doi", "")
            )
        
        # Preserve chart data
        edited["chart_data"] = safe_get(initial_content, "chart_data", None)
    
    # Render the abstract
    render_visual_abstract(edited)
    
    return edited


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Visual Abstract Generator",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 JACC-Style Visual Abstract")
    st.caption("AI-fillable template with editable content zones")
    
    # Sample content (this would come from AI agents)
    sample_content = {
        "title": "Effect of Exercise on Cardiovascular Mortality in Older Adults",
        "main_finding": "Regular physical activity was associated with a <highlight>42% reduction in cardiovascular mortality</highlight> among adults aged 65 and older, with benefits observed across all exercise intensity levels.",
        "background": "Cardiovascular disease remains the leading cause of death in older populations worldwide. While exercise is known to have protective effects, the optimal frequency, duration, and intensity for older adults has remained unclear.",
        "methods_summary": "Prospective Cohort Study",
        "participants": "10,847",
        "participants_label": "Adults aged 65+ followed for 10 years",
        "intervention": "Exercise",
        "intervention_label": "vs. Sedentary lifestyle",
        "methods_description": "Participants self-reported exercise habits at baseline and were followed via national health registries. Primary outcome was cardiovascular mortality. Analyses adjusted for age, sex, BMI, smoking, and comorbidities.",
        "results": [
            "42% lower CV mortality in active vs. sedentary (HR 0.58, 95% CI 0.52-0.65)",
            "Benefits observed with as little as 75 min/week moderate activity",
            "Dose-response: higher activity = greater protection",
            "No interaction with baseline health status"
        ],
        "chart_title": "Mortality Reduction",
        "chart_subtitle": "By Weekly Exercise Level",
        "chart_data": {"Low": 18, "Moderate": 31, "High": 42},
        "journal": "JACC",
        "year": "2024",
        "authors": "Johnson et al.",
        "doi": "10.1016/j.jacc.2024.01.001"
    }
    
    # Render with editing capability
    render_editable_abstract(sample_content)
