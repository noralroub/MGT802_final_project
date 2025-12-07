"""
Visual Abstract Template for Streamlit
JACC-style medical journal visual abstract renderer

Usage:
    from visual_abstract import render_visual_abstract
    
    render_visual_abstract(
        label="CENTRAL ILLUSTRATION",
        title="Your Study Title Here",
        hero_icon="heart",
        hero_text="Main finding text with <highlight>key outcomes</highlight> highlighted.",
        ...
    )
"""

import streamlit.components.v1 as components
from typing import List, Dict, Optional, Any


def get_icon_svg(icon_type: str) -> str:
    """Return SVG markup for various icons."""
    icons = {
        "heart": '''
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M50 90C50 90 10 60 10 35C10 20 22 10 35 10C43 10 50 15 50 15C50 15 57 10 65 10C78 10 90 20 90 35C90 60 50 90 50 90Z" fill="#8B0000" stroke="#ffffff" stroke-width="2"/>
                <path d="M30 40C30 40 35 50 50 55" stroke="#c41e3a" stroke-width="3" stroke-linecap="round"/>
                <circle cx="70" cy="35" r="8" fill="#c41e3a" opacity="0.5"/>
            </svg>
        ''',
        "brain": '''
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="50" cy="50" rx="35" ry="40" fill="#d4a84b" stroke="#ffffff" stroke-width="2"/>
                <path d="M50 15C50 15 35 25 35 50C35 75 50 85 50 85" stroke="#8B6914" stroke-width="2" fill="none"/>
                <path d="M35 35C25 35 20 45 25 55" stroke="#8B6914" stroke-width="2" fill="none"/>
                <path d="M65 35C75 35 80 45 75 55" stroke="#8B6914" stroke-width="2" fill="none"/>
                <path d="M30 55C20 60 25 75 40 70" stroke="#8B6914" stroke-width="2" fill="none"/>
                <path d="M70 55C80 60 75 75 60 70" stroke="#8B6914" stroke-width="2" fill="none"/>
            </svg>
        ''',
        "lungs": '''
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M50 15L50 45" stroke="#4a9b9b" stroke-width="4" stroke-linecap="round"/>
                <path d="M50 45L35 55L25 85C20 90 30 95 45 85L50 70" fill="#4a9b9b" stroke="#ffffff" stroke-width="2"/>
                <path d="M50 45L65 55L75 85C80 90 70 95 55 85L50 70" fill="#4a9b9b" stroke="#ffffff" stroke-width="2"/>
            </svg>
        ''',
        "pill": '''
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="25" y="35" width="50" height="30" rx="15" fill="#c41e3a" stroke="#ffffff" stroke-width="2"/>
                <line x1="50" y1="35" x2="50" y2="65" stroke="#ffffff" stroke-width="2"/>
                <rect x="50" y="35" width="25" height="30" rx="0" fill="#3b6fa0"/>
                <path d="M75 50A15 15 0 0 1 60 65L60 35A15 15 0 0 1 75 50Z" fill="#3b6fa0"/>
            </svg>
        ''',
        "dna": '''
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M30 10C30 10 70 30 70 50C70 70 30 90 30 90" stroke="#c41e3a" stroke-width="4" fill="none"/>
                <path d="M70 10C70 10 30 30 30 50C30 70 70 90 70 90" stroke="#3b6fa0" stroke-width="4" fill="none"/>
                <line x1="35" y1="25" x2="65" y2="25" stroke="#666666" stroke-width="2"/>
                <line x1="30" y1="50" x2="70" y2="50" stroke="#666666" stroke-width="2"/>
                <line x1="35" y1="75" x2="65" y2="75" stroke="#666666" stroke-width="2"/>
            </svg>
        ''',
        "microscope": '''
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="40" y="20" width="20" height="50" rx="2" fill="#1a2744"/>
                <circle cx="50" cy="75" r="10" fill="#4a9b9b" stroke="#1a2744" stroke-width="2"/>
                <rect x="25" y="85" width="50" height="5" rx="2" fill="#1a2744"/>
                <rect x="45" y="10" width="10" height="15" rx="2" fill="#3b6fa0"/>
                <circle cx="50" cy="35" r="5" fill="#d4a84b"/>
            </svg>
        ''',
        "people": '''
            <svg viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="25" cy="15" r="8" fill="#4a9b9b"/>
                <path d="M10 45C10 32 17 25 25 25C33 25 40 32 40 45" fill="#4a9b9b"/>
            </svg>
        ''',
        "randomize": '''
            <svg viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="15" cy="25" r="6" fill="#5b8cc9"/>
                <circle cx="35" cy="15" r="6" fill="#d4a84b"/>
                <circle cx="35" cy="35" r="6" fill="#c41e3a"/>
                <path d="M20 25L30 17M20 25L30 33" stroke="#1a2744" stroke-width="2"/>
            </svg>
        ''',
        "multicenter": '''
            <svg viewBox="0 0 24 24" fill="#4a9b9b">
                <circle cx="12" cy="12" r="10"/>
                <text x="12" y="16" text-anchor="middle" fill="white" font-size="10" font-weight="bold">M</text>
            </svg>
        ''',
        "calendar": '''
            <svg viewBox="0 0 24 24" fill="#1a2744">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <text x="12" y="15" text-anchor="middle" fill="white" font-size="7" font-weight="bold">30d</text>
            </svg>
        ''',
        "clock": '''
            <svg viewBox="0 0 24 24" fill="none" stroke="#1a2744" stroke-width="2">
                <circle cx="12" cy="12" r="10" fill="#f5f5f5"/>
                <path d="M12 6V12L16 14" stroke-linecap="round"/>
            </svg>
        ''',
        "chart": '''
            <svg viewBox="0 0 24 24" fill="#1a2744">
                <rect x="3" y="12" width="4" height="8"/>
                <rect x="10" y="6" width="4" height="14"/>
                <rect x="17" y="9" width="4" height="11"/>
            </svg>
        ''',
        "checkmark": '''
            <svg viewBox="0 0 24 24" fill="#22c55e">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 12L11 15L16 9" stroke="white" stroke-width="2" fill="none"/>
            </svg>
        ''',
    }
    return icons.get(icon_type, icons["heart"])


def render_visual_abstract(
    # Header
    label: str = "CENTRAL ILLUSTRATION",
    title: str = "Study Title Here",
    
    # Hero Section
    hero_icon: str = "heart",
    hero_text: str = "Main finding text with <highlight>key outcomes</highlight> highlighted.",
    
    # Left Column - Intro
    intro_text: str = "Background paragraph describing the study methodology and context.",
    section_title: str = "TRIAL DESIGN AND POPULATION",
    
    # Left Column - Stats
    stats: Optional[List[Dict]] = None,
    
    # Left Column - Icon Rows
    icon_rows: Optional[List[Dict]] = None,
    
    # Right Column - Results
    results_title: str = "RESULTS",
    primary_outcome: str = "Primary outcome = composite:",
    outcome_detail: str = "Outcome definition and details here.",
    outcome_items: Optional[List[Dict]] = None,
    
    # Right Column - Chart
    chart_title: str = "% Patients Who Experienced<br/>Primary Outcome",
    bar_data: Optional[List[Dict]] = None,
    
    # Footer
    footer: str = "Journal Year | Authors | Citation",
    
    # Display options
    show_chart: bool = True,
    show_results_box: bool = True,
    height: int = 700,
) -> None:
    """
    Render a JACC-style visual abstract in Streamlit.
    
    Parameters:
    -----------
    label : str
        Small label text in header (e.g., "CENTRAL ILLUSTRATION")
    title : str
        Main title in header bar
    hero_icon : str
        Icon type for hero section: "heart", "brain", "lungs", "pill", "dna", "microscope"
    hero_text : str
        Main finding text. Use <highlight>text</highlight> for gold highlighting
    intro_text : str
        Introductory paragraph in left column
    section_title : str
        Title for the section header pill (e.g., "TRIAL DESIGN AND POPULATION")
    stats : List[Dict]
        List of stat boxes. Each dict: {"value": "210", "label": "patients", "icon": "people"}
        Icon options: "people", "randomize", "chart", "clock", "checkmark"
    icon_rows : List[Dict]
        List of icon+text rows. Each dict: {"icon": "multicenter", "text": "Description"}
        Icon options: "multicenter", "calendar", "clock", "chart", "checkmark"
    results_title : str
        Title for results box header
    primary_outcome : str
        Primary outcome label text
    outcome_detail : str
        Detailed outcome description
    outcome_items : List[Dict]
        List of outcome items. Each dict: {"text": "Item text", "positive": False}
        positive=True shows checkmark, False shows X
    chart_title : str
        Title above bar chart (use <br/> for line breaks)
    bar_data : List[Dict]
        Bar chart data. Each dict: {"label": "Group", "value": 47, "n": 68, "color": "blue"}
        Color options: "blue", "red", "gray", "teal", "gold", "navy"
    footer : str
        Footer citation text
    show_chart : bool
        Whether to show the bar chart section
    show_results_box : bool
        Whether to show the results box
    height : int
        Height of the component in pixels
    """
    
    # Set defaults for mutable arguments
    if stats is None:
        stats = [
            {"value": "###", "label": "patients<br/>with condition", "icon": "people"},
            {"value": "Randomized", "label": "to treatment<br/>or placebo", "icon": "randomize"},
        ]
    
    if icon_rows is None:
        icon_rows = [
            {"icon": "multicenter", "text": "Multicenter"},
            {"icon": "calendar", "text": "30-day follow-up"},
        ]
    
    if outcome_items is None:
        outcome_items = [
            {"text": "Outcome item 1", "positive": False},
            {"text": "Outcome item 2", "positive": False},
        ]
    
    if bar_data is None:
        bar_data = [
            {"label": "Group 1", "value": 47, "n": 68, "color": "blue"},
            {"label": "Group 2", "value": 59, "n": 69, "color": "red"},
            {"label": "Placebo", "value": 53, "n": 70, "color": "gray"},
        ]
    
    # Build stats HTML
    stats_html = ""
    for stat in stats:
        stats_html += f'''
            <div class="va-stat-box">
                <div class="va-stat-icon">
                    {get_icon_svg(stat.get("icon", "people"))}
                </div>
                <div class="va-stat-value">{stat.get("value", "")}</div>
                <div class="va-stat-label">{stat.get("label", "")}</div>
            </div>
        '''
    
    # Build icon rows HTML
    icon_rows_html = ""
    for row in icon_rows:
        icon_rows_html += f'''
            <div class="va-icon-text-row">
                <div class="va-row-icon">
                    {get_icon_svg(row.get("icon", "multicenter"))}
                </div>
                <span class="va-row-text">{row.get("text", "")}</span>
            </div>
        '''
    
    # Build outcome items HTML
    outcome_items_html = ""
    for item in outcome_items:
        icon_class = "va-check-icon" if item.get("positive", False) else "va-x-icon"
        icon_char = "✓" if item.get("positive", False) else "✗"
        outcome_items_html += f'''
            <li><span class="{icon_class}">{icon_char}</span> {item.get("text", "")}</li>
        '''
    
    # Build bar chart HTML
    bar_chart_html = ""
    for bar in bar_data:
        bar_chart_html += f'''
            <div class="va-bar-row">
                <span class="va-bar-label">{bar.get("label", "")}</span>
                <div class="va-bar-container">
                    <div class="va-bar-fill {bar.get("color", "blue")}" style="width: {bar.get("value", 0)}%;">
                        {bar.get("value", 0)}%
                    </div>
                </div>
                <span class="va-bar-n">N = {bar.get("n", 0)}</span>
            </div>
        '''
    
    # Build results box HTML
    results_box_html = ""
    if show_results_box:
        results_box_html = f'''
            <div class="va-results-box">
                <div class="va-results-header">{results_title}</div>
                <div class="va-results-content">
                    <div class="va-primary-outcome">{primary_outcome}</div>
                    <div class="va-outcome-detail">{outcome_detail}</div>
                    <ul class="va-check-list">
                        {outcome_items_html}
                    </ul>
                </div>
            </div>
        '''
    
    # Build chart section HTML
    chart_section_html = ""
    if show_chart:
        chart_section_html = f'''
            <div class="va-chart-section">
                <div class="va-chart-title">{chart_title}</div>
                <div class="va-bar-chart">
                    {bar_chart_html}
                </div>
            </div>
        '''
    
    # Complete HTML with embedded styles
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: transparent;
                padding: 10px;
            }}
            
            .visual-abstract {{
                max-width: 800px;
                margin: 0 auto;
                background: #ffffff;
                border: 3px solid #1a2744;
                border-radius: 4px;
                overflow: hidden;
                line-height: 1.4;
            }}
            
            .va-header-bar {{
                background: #1a2744;
                color: #ffffff;
                padding: 8px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .va-header-bar .va-label {{
                background: #c41e3a;
                color: #ffffff;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                white-space: nowrap;
            }}
            
            .va-header-bar .va-title {{
                font-size: 13px;
                font-weight: 600;
            }}
            
            .va-hero-section {{
                background: linear-gradient(135deg, #c41e3a 0%, #9e1830 100%);
                color: #ffffff;
                padding: 24px;
                display: flex;
                align-items: center;
                gap: 24px;
            }}
            
            .va-hero-icon {{
                flex-shrink: 0;
                width: 80px;
                height: 80px;
            }}
            
            .va-hero-icon svg {{
                width: 100%;
                height: 100%;
            }}
            
            .va-hero-text {{
                font-size: 14px;
                line-height: 1.5;
            }}
            
            .va-hero-text highlight {{
                color: #d4a84b;
                font-weight: 600;
            }}
            
            .va-content-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
            }}
            
            .va-left-column {{
                padding: 24px;
                border-right: 1px solid #e0e0e0;
            }}
            
            .va-intro-text {{
                font-size: 12px;
                color: #666666;
                margin-bottom: 24px;
                line-height: 1.6;
            }}
            
            .va-section-header {{
                background: #1a2744;
                color: #ffffff;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                text-align: center;
                margin-bottom: 16px;
                letter-spacing: 0.5px;
            }}
            
            .va-stats-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-bottom: 24px;
            }}
            
            .va-stat-box {{
                text-align: center;
            }}
            
            .va-stat-icon {{
                width: 50px;
                height: 50px;
                margin: 0 auto 8px;
            }}
            
            .va-stat-icon svg {{
                width: 100%;
                height: 100%;
            }}
            
            .va-stat-value {{
                font-size: 18px;
                font-weight: 700;
                color: #1a2744;
            }}
            
            .va-stat-label {{
                font-size: 10px;
                color: #666666;
                line-height: 1.4;
            }}
            
            .va-icon-text-row {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;
            }}
            
            .va-row-icon {{
                width: 24px;
                height: 24px;
                flex-shrink: 0;
            }}
            
            .va-row-icon svg {{
                width: 100%;
                height: 100%;
            }}
            
            .va-row-text {{
                font-size: 11px;
                color: #666666;
            }}
            
            .va-right-column {{
                padding: 24px;
                background: #f5f5f5;
            }}
            
            .va-results-box {{
                background: #ffffff;
                border: 2px solid #c41e3a;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 24px;
            }}
            
            .va-results-header {{
                background: #c41e3a;
                color: #ffffff;
                padding: 4px 16px;
                margin: -16px -16px 16px -16px;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                text-align: center;
                letter-spacing: 0.5px;
            }}
            
            .va-results-content {{
                font-size: 11px;
            }}
            
            .va-primary-outcome {{
                color: #c41e3a;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .va-outcome-detail {{
                color: #666666;
                margin-bottom: 8px;
            }}
            
            .va-check-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .va-check-list li {{
                display: flex;
                align-items: flex-start;
                gap: 4px;
                margin-bottom: 4px;
                font-size: 11px;
                color: #666666;
            }}
            
            .va-check-icon {{
                color: #22c55e;
                font-weight: 700;
                flex-shrink: 0;
            }}
            
            .va-x-icon {{
                color: #c41e3a;
                font-weight: 700;
                flex-shrink: 0;
            }}
            
            .va-chart-section {{
                background: #ffffff;
                border-radius: 8px;
                padding: 16px;
            }}
            
            .va-chart-title {{
                font-size: 11px;
                font-weight: 700;
                color: #1a2744;
                text-align: center;
                margin-bottom: 16px;
                line-height: 1.4;
            }}
            
            .va-bar-chart {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            
            .va-bar-row {{
                display: grid;
                grid-template-columns: 70px 1fr 50px;
                align-items: center;
                gap: 8px;
            }}
            
            .va-bar-label {{
                font-size: 10px;
                color: #666666;
                text-align: right;
            }}
            
            .va-bar-container {{
                height: 20px;
                background: #e8e8e8;
                border-radius: 4px;
                overflow: hidden;
                position: relative;
            }}
            
            .va-bar-fill {{
                height: 100%;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #ffffff;
                font-size: 10px;
                font-weight: 700;
                transition: width 0.5s ease;
            }}
            
            .va-bar-fill.blue {{ background: #3b6fa0; }}
            .va-bar-fill.red {{ background: #c41e3a; }}
            .va-bar-fill.gray {{ background: #7a8899; }}
            .va-bar-fill.teal {{ background: #4a9b9b; }}
            .va-bar-fill.gold {{ background: #d4a84b; }}
            .va-bar-fill.navy {{ background: #1a2744; }}
            
            .va-bar-n {{
                font-size: 10px;
                color: #666666;
            }}
            
            .va-footer {{
                background: #1a2744;
                color: #ffffff;
                padding: 8px 16px;
                font-size: 8px;
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="visual-abstract">
            <div class="va-header-bar">
                <span class="va-label">{label}</span>
                <span class="va-title">{title}</span>
            </div>
            
            <div class="va-hero-section">
                <div class="va-hero-icon">
                    {get_icon_svg(hero_icon)}
                </div>
                <div class="va-hero-text">
                    {hero_text}
                </div>
            </div>
            
            <div class="va-content-grid">
                <div class="va-left-column">
                    <p class="va-intro-text">{intro_text}</p>
                    
                    <div class="va-section-header">{section_title}</div>
                    
                    <div class="va-stats-grid">
                        {stats_html}
                    </div>
                    
                    {icon_rows_html}
                </div>
                
                <div class="va-right-column">
                    {results_box_html}
                    {chart_section_html}
                </div>
            </div>
            
            <div class="va-footer">{footer}</div>
        </div>
    </body>
    </html>
    '''
    
    # Use components.html for proper rendering
    components.html(html, height=height, scrolling=True)


def render_blank_template(height: int = 700) -> None:
    """Render a blank visual abstract template with placeholder text."""
    render_visual_abstract(
        label="[LABEL]",
        title="[Study Title Goes Here]",
        hero_icon="heart",
        hero_text="[Main finding or conclusion. Use <highlight>highlighted text</highlight> for key outcomes.]",
        intro_text="[Introductory paragraph describing study background and methodology.]",
        section_title="[SECTION TITLE]",
        stats=[
            {"value": "[###]", "label": "[Description<br/>line 2]", "icon": "people"},
            {"value": "[Label]", "label": "[Description<br/>line 2]", "icon": "randomize"},
        ],
        icon_rows=[
            {"icon": "multicenter", "text": "[Row description]"},
            {"icon": "calendar", "text": "[Row description]"},
        ],
        results_title="RESULTS",
        primary_outcome="[Primary outcome label]",
        outcome_detail="[Outcome definition and details]",
        outcome_items=[
            {"text": "[Outcome item 1]", "positive": False},
            {"text": "[Outcome item 2]", "positive": False},
            {"text": "[Outcome item 3]", "positive": False},
        ],
        chart_title="[Chart Title<br/>Subtitle]",
        bar_data=[
            {"label": "[Group 1]", "value": 47, "n": 68, "color": "blue"},
            {"label": "[Group 2]", "value": 59, "n": 69, "color": "red"},
            {"label": "[Group 3]", "value": 53, "n": 70, "color": "gray"},
        ],
        footer="[Journal] [Year] | [Authors] | [Citation]",
        height=height
    )


def _format_number(value: Any) -> str:
    """Return value formatted as string with commas when numeric."""
    if isinstance(value, (int, float)):
        return f"{value:,}"
    if value is None:
        return "n/a"
    return str(value)


def _safe_percentage(value: Any) -> Optional[float]:
    """Convert values like '45%' to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def render_visual_abstract_from_trial(trial_data: Dict[str, Any], height: int = 750) -> None:
    """Convenience helper that maps extracted trial data into the template."""
    if not trial_data:
        render_blank_template(height=height)
        return

    trial = trial_data.get("trial_info", {})
    population = trial_data.get("population", {})
    primary = trial_data.get("primary_outcome", {})
    events = trial_data.get("event_rates", {})
    adverse = trial_data.get("adverse_events", {})
    dosing = trial_data.get("dosing", {})
    conclusions = trial_data.get("conclusions") or []

    label = (trial.get("trial_name") or trial.get("drug") or "STUDY").upper()
    title = trial.get("title") or "Clinical Trial Visual Abstract"
    hero_text = conclusions[0] if conclusions else "Key finding not provided."

    total = _format_number(population.get("total_enrolled"))
    mean_age = _format_number(population.get("age_mean"))
    stats = [
        {"value": total, "label": "Total<br/>participants", "icon": "people"},
        {"value": mean_age, "label": "Mean age<br/>(years)", "icon": "clock"},
    ]

    intro_text = (
        f"{title} evaluated {trial.get('drug', 'the intervention')} "
        f"for {trial.get('indication', 'the condition')} across "
        f"{total} participants."
    )

    icon_rows = []
    dosing_text = dosing.get("description")
    if dosing_text:
        icon_rows.append({"icon": "multicenter", "text": dosing_text})
    summary_text = adverse.get("summary")
    if summary_text:
        icon_rows.append({"icon": "calendar", "text": summary_text})
    if not icon_rows:
        icon_rows = [
            {"icon": "multicenter", "text": "Study details unavailable"},
        ]

    outcome_items: List[Dict[str, Any]] = []
    for item in (adverse.get("notable") or [])[:3]:
        outcome_items.append({"text": item, "positive": False})
    if not outcome_items:
        for item in conclusions[:3]:
            outcome_items.append({"text": item, "positive": True})
    if not outcome_items:
        outcome_items = [{"text": "No additional findings provided.", "positive": True}]

    bar_data = []
    arm1_pct = _safe_percentage(events.get("arm_1_percent"))
    arm2_pct = _safe_percentage(events.get("arm_2_percent"))
    if arm1_pct is not None:
        bar_data.append({
            "label": population.get("arm_1_label", "Group 1"),
            "value": int(round(arm1_pct)),
            "n": _format_number(population.get("arm_1_size")),
            "color": "blue",
        })
    if arm2_pct is not None:
        bar_data.append({
            "label": population.get("arm_2_label", "Group 2"),
            "value": int(round(arm2_pct)),
            "n": _format_number(population.get("arm_2_size")),
            "color": "red",
        })
    if not bar_data:
        bar_data = [
            {"label": "Group 1", "value": 50, "n": "n/a", "color": "blue"},
            {"label": "Group 2", "value": 40, "n": "n/a", "color": "red"},
        ]

    outcome_detail = " | ".join(
        filter(
            None,
            [
                f"Effect: {primary.get('effect_measure')}" if primary.get("effect_measure") else "",
                f"Estimate: {primary.get('estimate')}" if primary.get("estimate") else "",
                f"CI: {primary.get('ci')}" if primary.get("ci") else "",
                f"P: {primary.get('p_value')}" if primary.get("p_value") else "",
            ],
        )
    ) or "Outcome details not available."

    render_visual_abstract(
        label=label,
        title=title,
        hero_icon="heart",
        hero_text=hero_text,
        intro_text=intro_text,
        section_title="TRIAL DESIGN AND POPULATION",
        stats=stats,
        icon_rows=icon_rows,
        results_title="RESULTS",
        primary_outcome=primary.get("label", "Primary outcome"),
        outcome_detail=outcome_detail,
        outcome_items=outcome_items,
        chart_title="Event Rates",
        bar_data=bar_data,
        footer=f"{trial.get('publication', 'Journal')} | {trial.get('trial_name', '')}",
        height=height,
    )
