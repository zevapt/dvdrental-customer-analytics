"""
app.py
Customer Behavior & Revenue Analytics Dashboard
Entry point - sidebar navigation, global styles, DB health check.

Run with:
    streamlit run app.py
"""
import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.connection import check_connection
from dashboard.styles import inject_styles
from dashboard.components import connection_status_badge

import dashboard.pages.overview         as pg_overview
import dashboard.pages.customers        as pg_customers
import dashboard.pages.insights         as pg_insights
import dashboard.pages.customer_profile as pg_profile

# ── Inject global CSS ──────────────────────────────────────────────────────────
inject_styles()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem 0;text-align:center;">
        <div style="font-size:2rem;">📊</div>
        <div style="font-family:'DM Serif Display',serif;font-size:1rem;
                    color:#E8EDF5;margin-top:0.25rem;">Analytics Dashboard</div>
        <div style="font-size:0.7rem;color:#6B8DD6;margin-top:0.15rem;">
            dvdrental · PostgreSQL
        </div>
    </div>
    """, unsafe_allow_html=True)

    ok = check_connection()
    connection_status_badge(ok)
    st.markdown("<br>", unsafe_allow_html=True)

    page = st.radio(
        "Navigate to",
        options=[
            "🏠  Executive Overview",
            "👥  Customer Intelligence",
            "⚠  Strategic Insights",
            "🔍  Customer Details",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.7rem;color:#4A5A7A;text-align:center;line-height:1.6;'>"
        "PostgreSQL · dvdrental<br>"
        "Python · Streamlit · Plotly<br>scikit-learn · SQLAlchemy"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Offline guard ──────────────────────────────────────────────────────────────
if not ok:
    st.error(
        "⚠ Cannot connect to PostgreSQL. "
        "Check your `.env` file and ensure the dvdrental database is running."
    )
    st.code(
        "# Quick start:\n"
        "createdb dvdrental\n"
        "psql dvdrental < restore.sql\n\n"
        "# Then update .env with your credentials and restart.",
        language="bash",
    )
    st.stop()

# ── Page routing ───────────────────────────────────────────────────────────────
if   "Overview"   in page: pg_overview.render()
elif "Customer I" in page: pg_customers.render()
elif "Insights"   in page: pg_insights.render()
elif "Details"    in page: pg_profile.render()
