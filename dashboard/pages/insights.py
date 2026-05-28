"""
dashboard/pages/insights.py
Strategic Insights & Risk Analysis page.
At-risk customer table + dynamically generated executive insight cards.
"""
import streamlit as st
import pandas as pd

from analytics.insights import get_at_risk_customers, generate_insights
from analytics.behavior import get_rentals_vs_revenue
from analytics.rfm import get_rfm_data
from dashboard.components import section_header, render_insight_cards, export_csv_button
from config.settings import COLORS


def render():
    section_header("STRATEGIC INSIGHTS", "Risk Detection & Executive Intelligence")

    with st.spinner("Loading insights data…"):
        at_risk_df  = get_at_risk_customers()
        scatter_df  = get_rentals_vs_revenue()
        rfm_df      = get_rfm_data()
        insights    = generate_insights(scatter_df, rfm_df)

    # ── Key Insight Cards ─────────────────────────────────────────────────────
    st.markdown(
        "<p style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;"
        "color:#D05C78;font-weight:700;margin-bottom:0.5rem;'>KEY INSIGHTS</p>",
        unsafe_allow_html=True,
    )
    render_insight_cards(insights)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── At-Risk Customer Table ─────────────────────────────────────────────────
    n_at_risk = len(at_risk_df)
    st.markdown(
        f"<p style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;"
        f"color:#D05C78;font-weight:700;margin-bottom:0.5rem;'>⚠ AT-RISK CUSTOMERS</p>",
        unsafe_allow_html=True,
    )

    if at_risk_df.empty:
        st.info("No at-risk customers found.")
        return

    st.markdown(
        f"<div style='background:#FFF8E7;border:1px solid #F0A500;border-radius:8px;"
        f"padding:0.6rem 1rem;font-size:0.85rem;color:#8A6000;margin-bottom:0.75rem;'>"
        f"⚠ <strong>{n_at_risk}</strong> customers haven't rented in 90+ days.</div>",
        unsafe_allow_html=True,
    )

    # Churn risk filter
    risk_filter = st.radio(
        "Filter by churn risk:", ["All", "High", "Medium", "Low"],
        horizontal=True,
    )
    display_df = (
        at_risk_df if risk_filter == "All"
        else at_risk_df[at_risk_df["churn_risk"] == risk_filter]
    )

    # Styled table
    def color_risk(val):
        colors_map = {"High": "#C0392B", "Medium": "#E67E22", "Low": "#27AE60"}
        return f"color: {colors_map.get(val, 'inherit')}; font-weight: 600"

    styled = (
        display_df[[
            "customer_name", "email", "last_rental_date",
            "total_rentals", "total_spent", "days_inactive", "churn_risk"
        ]]
        .rename(columns={
            "customer_name":   "Customer",
            "email":           "Email",
            "last_rental_date":"Last Rental",
            "total_rentals":   "Total Rentals",
            "total_spent":     "Total Spent ($)",
            "days_inactive":   "Days Inactive",
            "churn_risk":      "Churn Risk",
        })
        .style
        .applymap(color_risk, subset=["Churn Risk"])
        .format({"Total Spent ($)": "${:.2f}"})
    )

    st.dataframe(styled, use_container_width=True, hide_index=True, height=350)
    export_csv_button(display_df, "at_risk_customers.csv", "⬇ Export At-Risk List")
