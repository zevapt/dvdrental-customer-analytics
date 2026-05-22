"""
dashboard/components.py
Reusable UI components: hero header, KPI cards, section headers,
insight cards, data table with export, customer profile header.
"""
import pandas as pd
import streamlit as st


def render_hero():
    st.markdown("""
    <div class="hero-header">
        <h1>📊 Customer Analytics Dashboard</h1>
        <p>Revenue · Behavior · Loyalty · Segmentation - powered by dvdrental data</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(kpis: dict):
    """Renders five KPI cards in a responsive row."""
    cols = st.columns(5)
    cards = [
        ("TOTAL CUSTOMERS",   f"{kpis.get('total_customers', 0):,}",   "active customers",      ""),
        ("TOTAL REVENUE",     f"${kpis.get('total_revenue', 0):,.2f}", "all transactions",      ""),
        ("TOTAL RENTALS",     f"{kpis.get('total_rentals', 0):,}",     "all time",              "blue"),
        ("AVG TRANSACTION",   f"${kpis.get('avg_transaction_value', 0):.2f}", "per payment",   "blue"),
        ("AVG SPEND/CUSTOMER",f"${kpis.get('avg_clv', 0):.2f}",        "lifetime value",        "navy"),
    ]
    for col, (label, value, sub, cls) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="kpi-card {cls}">
                <div class="kpi-card-label">{label}</div>
                <div class="kpi-card-value">{value}</div>
                <div class="kpi-card-sub">● {sub}</div>
            </div>
            """, unsafe_allow_html=True)


def section_header(tag: str, title: str):
    st.markdown(f'<div class="section-tag">{tag}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def render_insight_cards(insights: list[dict]):
    """Renders 3 dynamic business insight cards in a row."""
    cols = st.columns(3)
    for col, ins in zip(cols, insights):
        with col:
            st.markdown(f"""
            <div class="insight-card">
                <div class="section-tag">{ins['title']}</div>
                <div class="insight-metric" style="color:{ins['color']}">{ins['metric']}</div>
                <div class="insight-desc">{ins['description']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_customer_profile_header(stats: dict):
    status_color = "#27AE60" if stats.get("status") == "Active" else "#E74C3C"
    st.markdown(f"""
    <div class="profile-header">
        <div style="font-size:2.5rem">👤</div>
        <div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.4rem">
                {stats.get('customer_name', '')}
            </div>
            <div style="font-size:0.8rem;color:#A8B4C8;margin-top:0.25rem">
                ✉ {stats.get('email', '')} &nbsp;|&nbsp;
                🌍 {stats.get('country', '')} &nbsp;|&nbsp;
                <span style="color:{status_color}">● {stats.get('status', '')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def export_csv_button(df: pd.DataFrame, filename: str, label: str = "⬇ Download CSV"):
    """Adds a CSV export button below a dataframe."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv,
                       file_name=filename, mime="text/csv")


def connection_status_badge(ok: bool):
    if ok:
        st.sidebar.markdown(
            '<div style="background:#1D4A2E;color:#27AE60;padding:0.4rem 0.8rem;'
            'border-radius:8px;font-size:0.75rem;font-weight:600;text-align:center;">'
            '● PostgreSQL Connected</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            '<div style="background:#4A1D1D;color:#E74C3C;padding:0.4rem 0.8rem;'
            'border-radius:8px;font-size:0.75rem;font-weight:600;text-align:center;">'
            '✕ Database Offline</div>', unsafe_allow_html=True)
