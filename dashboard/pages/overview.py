"""
dashboard/pages/overview.py
Hero Header + KPI Overview page.
"""
import streamlit as st
import plotly.graph_objects as go

from analytics.kpi import get_kpis
from analytics.revenue import get_monthly_revenue
from dashboard.components import render_hero, render_kpi_cards, section_header, export_csv_button
from config.settings import COLORS


def render():
    render_hero()
    section_header("KEY METRICS", "Business Overview")

    with st.spinner("Loading KPIs…"):
        kpis = get_kpis()

    if not kpis:
        st.error("Could not load KPIs. Check database connection.")
        return

    render_kpi_cards(kpis)

    st.markdown("<br><br>", unsafe_allow_html=True)

    section_header("REVENUE TREND", "Monthly Revenue & Transactions")

    st.markdown(
        "<p style='color:#6B7A8D;font-size:0.85rem;margin-top:-0.5rem;margin-bottom:1rem;'>"
        "Total payment collected per month - filtered by sidebar date range</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading revenue data…"):
        df = get_monthly_revenue()

    if df.empty:
        st.warning("No revenue data available.")
        return
    
    ALIGNMENT_RATIO = 25000 / 6000 
    max_revenue_data = df["revenue"].max()
    yaxis_max_revenue = max_revenue_data * 1.15
    yaxis2_max_transactions = yaxis_max_revenue / ALIGNMENT_RATIO

    # ── Chart ──────────────────────────────────────────────────────────────────
    fig = go.Figure()

    # Bar: transaction volume (secondary y)
    fig.add_trace(go.Bar(
        x=df["month_label"],
        y=df["transactions"],
        name="Transactions",
        marker_color=COLORS["accent2"],
        opacity=0.55,
        yaxis="y2",
    ))

    # Line: revenue (primary y)
    fig.add_trace(go.Scatter(
        x=df["month_label"],
        y=df["revenue"],
        name="Revenue",
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=3, shape="spline"),
        marker=dict(size=8, color=COLORS["accent"], line=dict(width=2, color="white")),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
    ))

    # Annotation for peak month
    if not df.empty:
        peak = df.loc[df["revenue"].idxmax()]
        fig.add_annotation(
            x=peak["month_label"],
            y=peak["revenue"],
            text=f"Peak: ${peak['revenue']:,.0f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLORS["accent"],
            font=dict(size=11, color=COLORS["accent"]),
            bgcolor="white",
            bordercolor=COLORS["accent"],
            borderwidth=1,
            yanchor="bottom",
            ay=-40,
        )

    fig.update_layout(
        title=dict(text="Monthly Revenue & Transactions",
                   font=dict(family="DM Serif Display", size=18, color=COLORS["primary"])),
        xaxis=dict(title="", showgrid=False),
        # FIXED: Added explicit range bound to lock the scales together
        yaxis=dict(title="Revenue ($)", tickprefix="$", showgrid=True,
                   gridcolor="#F0F2F5", range=[0, yaxis_max_revenue]),
        # FIXED: Added explicit range bound matching your ratio
        yaxis2=dict(title="Transactions", overlaying="y", side="right",
                    showgrid=False, range=[0, yaxis2_max_transactions]),
        legend=dict(orientation="h", y=1.12, x=0.7),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=60, t=60, b=40),
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── MoM growth table ───────────────────────────────────────────────────────
    with st.expander("Month-over-Month Growth Detail"):
        display = df[["month_label", "revenue", "transactions", "mom_growth_pct"]].copy()
        display.columns = ["Month", "Revenue ($)", "Transactions", "MoM Growth (%)"]
        display["Revenue ($)"] = display["Revenue ($)"].map("${:,.2f}".format)
        st.dataframe(display, use_container_width=True, hide_index=True)
        export_csv_button(df, "monthly_revenue.csv")


