"""
dashboard/styles.py
Global CSS injection for the Streamlit dashboard.
Targets the Streamlit DOM structure with class overrides.
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --primary:   #1B2A4A;
    --accent:    #D05C78;
    --accent2:   #6B8DD6;
    --neutral:   #A8B4C8;
    --surface:   #F5F7FA;
    --card-bg:   #FFFFFF;
    --text:      #1B2A4A;
    --muted:     #6B7A8D;
    --radius:    12px;
    --shadow:    0 2px 16px rgba(27,42,74,0.08);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--primary) !important;
}
[data-testid="stSidebar"] * {
    color: #E8EDF5 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label {
    color: #A8B4C8 !important;
    font-size: 0.75rem !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, var(--primary) 0%, #2D4170 100%);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: #FFFFFF;
}
.hero-header h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2rem;
    margin: 0 0 0.25rem 0;
    color: #FFFFFF;
}
.hero-header p {
    color: #A8B4C8;
    margin: 0;
    font-size: 0.9rem;
}

/* KPI cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    border-top: 3px solid var(--accent);
}
.kpi-card.blue  { border-top-color: var(--accent2); }
.kpi-card.navy  { border-top-color: var(--primary); }
.kpi-card-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.kpi-card-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.7rem;
    color: var(--text);
    line-height: 1;
}
.kpi-card-sub {
    font-size: 0.75rem;
    color: var(--accent);
    margin-top: 0.35rem;
}
.kpi-card.blue  .kpi-card-sub { color: var(--accent2); }
.kpi-card.navy  .kpi-card-sub { color: var(--primary); }

/* Section headers */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--primary);
    margin: 1.5rem 0 0.25rem 0;
    border-bottom: 2px solid var(--surface);
    padding-bottom: 0.5rem;
}
.section-tag {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 0.1rem;
}

/* Insight cards */
.insight-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    height: 100%;
}
.insight-metric {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    line-height: 1;
    margin: 0.5rem 0;
}
.insight-desc {
    font-size: 0.82rem;
    color: var(--muted);
    line-height: 1.5;
}

/* Risk table conditional colors */
.risk-high   { color: #C0392B; font-weight: 600; }
.risk-medium { color: #E67E22; font-weight: 600; }
.risk-low    { color: #27AE60; font-weight: 600; }

/* Customer profile header */
.profile-header {
    background: var(--primary);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 1rem;
}

/* ML badge */
.ml-badge {
    display: inline-block;
    background: var(--accent2);
    color: white;
    font-size: 0.65rem;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    vertical-align: middle;
    margin-left: 0.5rem;
}

/* Streamlit overrides */
[data-testid="metric-container"] {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow);
}
div[data-testid="stDataFrame"] {
    border-radius: var(--radius);
    overflow: hidden;
}
.stButton > button {
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-weight: 500;
}
.stButton > button:hover {
    background: var(--accent);
}
</style>
"""


def inject_styles():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
