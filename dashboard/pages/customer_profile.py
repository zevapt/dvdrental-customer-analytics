"""
dashboard/pages/customer_profile.py
Individual Customer Profiling page.
Search → select → full behavioral deep-dive.
"""
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from analytics.customers import get_all_customers
from database.connection import run_query
from dashboard.components import section_header, render_customer_profile_header, export_csv_button
from config.settings import COLORS

# ── Per-customer SQL ──────────────────────────────────────────────────────────
STATS_SQL = """
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name          AS customer_name,
    c.email,
    co.country,
    COUNT(DISTINCT r.rental_id)                  AS total_rentals,
    ROUND(SUM(p.amount)::NUMERIC, 2)             AS total_spent,
    ROUND(AVG(p.amount)::NUMERIC, 2)             AS avg_transaction,
    MIN(r.rental_date)::DATE                     AS first_rental,
    MAX(r.rental_date)::DATE                     AS last_rental,
    CASE WHEN c.activebool THEN 'Active' ELSE 'Inactive' END AS status
FROM customer  c
JOIN rental    r  ON c.customer_id = r.customer_id
JOIN payment   p  ON r.rental_id   = p.rental_id
JOIN address   a  ON c.address_id  = a.address_id
JOIN city      ci ON a.city_id     = ci.city_id
JOIN country   co ON ci.country_id = co.country_id
WHERE c.customer_id = :cid
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, co.country, c.activebool
"""

ACTIVITY_SQL = """
SELECT
    DATE_TRUNC('month', r.rental_date)::DATE AS month,
    COUNT(*)                                  AS rentals
FROM rental r
WHERE r.customer_id = :cid
GROUP BY 1
ORDER BY 1
"""

GENRE_SQL = """
SELECT
    cat.name                      AS genre,
    COUNT(DISTINCT r.rental_id)   AS rentals
FROM rental       r
JOIN inventory    i   ON r.inventory_id = i.inventory_id
JOIN film         f   ON i.film_id      = f.film_id
JOIN film_category fc ON f.film_id      = fc.film_id
JOIN category     cat ON fc.category_id = cat.category_id
WHERE r.customer_id = :cid
GROUP BY cat.name
ORDER BY rentals DESC
"""

PAYMENT_TREND_SQL = """
SELECT
    DATE_TRUNC('month', p.payment_date)::DATE AS month,
    ROUND(SUM(p.amount)::NUMERIC, 2)           AS monthly_spend
FROM payment p
WHERE p.customer_id = :cid
GROUP BY 1
ORDER BY 1
"""


def render():
    section_header("DEEP DIVE", "Individual Customer Profiling")
    st.markdown(
        "<p style='color:#6B7A8D;font-size:0.85rem;margin-top:-0.5rem;margin-bottom:1rem;'>"
        "Search a customer and explore their full rental history &amp; preferences.</p>",
        unsafe_allow_html=True,
    )

    # ── Customer search ────────────────────────────────────────────────────────
    customers = get_all_customers()

    search = st.text_input("🔍 Search Customer Name", value="", placeholder="e.g. Eleanor")
    filtered = customers[
        customers["customer_name"].str.contains(search, case=False, na=False)
    ] if search else customers

    if filtered.empty:
        st.warning("No customers match your search.")
        return

    options = filtered.apply(
        lambda r: f"{r['customer_name']} (ID {r['customer_id']})", axis=1
    ).tolist()
    selected_label = st.selectbox("Select Customer", options)
    cid = int(selected_label.split("(ID ")[1].rstrip(")"))

    # ── Load profile data ──────────────────────────────────────────────────────
    with st.spinner(f"Loading profile for customer {cid}…"):
        stats_df    = run_query(STATS_SQL,    {"cid": cid})
        activity_df = run_query(ACTIVITY_SQL, {"cid": cid})
        genre_df    = run_query(GENRE_SQL,    {"cid": cid})
        payment_df  = run_query(PAYMENT_TREND_SQL, {"cid": cid})

    if stats_df.empty:
        st.error("No data found for this customer.")
        return

    stats = stats_df.iloc[0].to_dict()
    render_customer_profile_header(stats)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Mini KPI row ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_items = [
        ("TOTAL RENTALS",   str(stats["total_rentals"]),     "rentals"),
        ("TOTAL SPENT",     f"${stats['total_spent']:.2f}",  "lifetime"),
        ("AVG TRANSACTION", f"${stats['avg_transaction']:.2f}", "per payment"),
        ("FIRST RENTAL",    str(stats["first_rental"]),      "joined"),
        ("LAST RENTAL",     str(stats["last_rental"]),       "most recent"),
    ]
    for col, (label, val, sub) in zip([c1,c2,c3,c4,c5], kpi_items):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:1rem;
                        box-shadow:0 2px 12px rgba(27,42,74,0.06);
                        border-top:2px solid #D05C78;">
                <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
                            color:#6B7A8D;font-weight:600;">{label}</div>
                <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;
                            color:#1B2A4A;margin:0.3rem 0;">{val}</div>
                <div style="font-size:0.72rem;color:#D05C78;">● {sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Activity & Genre charts ────────────────────────────────────────────────
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("<strong style='font-size:0.9rem;color:#1B2A4A'>Rental Activity Over Time</strong><br>"
                    "<span style='font-size:0.78rem;color:#6B7A8D'>How active has this customer been?</span>",
                    unsafe_allow_html=True)
        if not activity_df.empty:
            activity_df["month"] = pd.to_datetime(activity_df["month"])
            activity_df["month_label"] = activity_df["month"].dt.strftime("%b %Y")
            fig_act = go.Figure(go.Scatter(
                x=activity_df["month_label"], y=activity_df["rentals"],
                mode="lines+markers",
                line=dict(color=COLORS["primary"], width=2.5),
                marker=dict(size=7, color=COLORS["accent"], line=dict(width=1.5, color="white")),
                fill="tozeroy", fillcolor="rgba(27,42,74,0.07)",
                hovertemplate="%{x}: %{y} rentals<extra></extra>",
            ))
            fig_act.update_layout(
                height=280, margin=dict(l=40,r=20,t=10,b=40),
                xaxis=dict(showgrid=False),
                yaxis=dict(title="Rentals", showgrid=True, gridcolor="#F0F2F5"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_act, use_container_width=True)

    with col_b:
        st.markdown("<strong style='font-size:0.9rem;color:#1B2A4A'>Favorite Genres</strong><br>"
                    "<span style='font-size:0.78rem;color:#6B7A8D'>What does this customer love to watch?</span>",
                    unsafe_allow_html=True)
        if not genre_df.empty:
            n = len(genre_df)
            gcolors = [f"rgba(27,42,74,{0.3 + 0.7*i/max(n-1,1)})" for i in range(n)]
            gcolors[0] = COLORS["accent"]   # top genre in accent
            fig_genre = go.Figure(go.Bar(
                x=genre_df["rentals"],
                y=genre_df["genre"],
                orientation="h",
                marker_color=gcolors,
                text=genre_df["rentals"],
                textposition="outside",
            ))
            fig_genre.update_layout(
                height=280, margin=dict(l=10,r=40,t=10,b=10),
                xaxis=dict(title="Rentals", showgrid=True, gridcolor="#F0F2F5"),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_genre, use_container_width=True)

    # ── Spending trend ─────────────────────────────────────────────────────────
    if not payment_df.empty:
        payment_df["month"] = pd.to_datetime(payment_df["month"])
        payment_df["month_label"] = payment_df["month"].dt.strftime("%b %Y")
        fig_spend = go.Figure(go.Bar(
            x=payment_df["month_label"], y=payment_df["monthly_spend"],
            marker_color=COLORS["accent2"], opacity=0.85,
            text=payment_df["monthly_spend"].map("${:.2f}".format),
            textposition="outside",
        ))
        fig_spend.update_layout(
            title=dict(text="Monthly Spending Trend",
                       font=dict(family="DM Serif Display", size=15, color=COLORS["primary"])),
            height=280, margin=dict(l=60,r=20,t=40,b=40),
            xaxis=dict(showgrid=False),
            yaxis=dict(title="Spend ($)", tickprefix="$", showgrid=True, gridcolor="#F0F2F5"),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig_spend, use_container_width=True)

    # ── Narrative ──────────────────────────────────────────────────────────────
    fav_genre = genre_df.iloc[0]["genre"] if not genre_df.empty else "-"
    st.markdown(f"""
    <div style="background:#F5F7FA;border-radius:12px;padding:1.25rem 1.5rem;
                border-left:4px solid #6B8DD6;margin-top:0.5rem;">
        <strong style="color:#1B2A4A;">Personalisation Opportunity</strong><br>
        <span style="font-size:0.88rem;color:#6B7A8D;line-height:1.7">
        <strong>{stats['customer_name']}</strong> has spent
        <strong>${stats['total_spent']:.2f}</strong> across
        <strong>{stats['total_rentals']}</strong> rentals with a favourite genre of
        <strong>{fav_genre}</strong>.
        Targeted campaigns featuring new <em>{fav_genre}</em> releases,
        exclusive pre-access, or a loyalty reward at their next rental milestone
        would resonate strongly with this customer's demonstrated preferences.
        </span>
    </div>
    """, unsafe_allow_html=True)
