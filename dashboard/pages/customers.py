"""
dashboard/pages/customers.py
Customer Overview: Top 10 customers + distribution by country.
"""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from analytics.customers import get_top_customers, get_customers_by_country
from analytics.behavior import get_genre_popularity, get_rentals_vs_revenue
from analytics.insights import get_correlation
from analytics.rfm import get_rfm_data, get_spending_tiers
from ml.clustering import fit_clusters, cluster_summary
from dashboard.components import render_hero, section_header, export_csv_button
from config.settings import COLORS, SPENDING_TIER_COLORS

SEGMENT_COLORS = {
    "Champions":           COLORS["champions"],
    "Loyal Customers":     COLORS["loyal"],
    "Potential Loyalists": COLORS["potential"],
    "At Risk":             COLORS["at_risk"],
    "Lost Customers":      COLORS["neutral"],
}

def render():
    tab1, tab2 = st.tabs([
        "Customer Analytics",
        "Segmentation & ML"
    ])

    with tab1:
        section_header("CUSTOMER OVERVIEW", "Top 10 Customers & Geographic Distribution")

        with st.spinner("Loading customer data…"):
            top_df    = get_top_customers()
            country_df = get_customers_by_country()

        col_left, col_right = st.columns(2, gap="large")

        # ── Top 10 Customers ──────────────────────────────────────────────────────
        with col_left:
            st.markdown(
                "<strong style='font-size:0.95rem;color:#1B2A4A'>Top 10 Customers by Spending</strong><br>"
                f"<span style='font-size:0.78rem;color:#D05C78'>Top 10 customers contribute "
                f"<strong>{_top10_share(top_df)}%</strong> of filtered revenue</span>",
                unsafe_allow_html=True,
            )

            colors = [COLORS["accent"] if i == 0 else COLORS["primary"]
                    for i in range(len(top_df))]

            fig_top = go.Figure(go.Bar(
                x=top_df["total_spent"],
                y=top_df["customer_name"],
                orientation="h",
                marker_color=colors,
                text=top_df["total_spent"].map("${:,.0f}".format),
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Total Spent: $%{x:,.2f}<br>"
                    "Rentals: %{customdata[0]}<br>"
                    "Avg Transaction: $%{customdata[1]:.2f}"
                    "<extra></extra>"
                ),
                customdata=top_df[["total_rentals", "avg_transaction"]].values,
            ))
            fig_top.update_layout(
                height=380, margin=dict(l=10, r=60, t=10, b=10),
                xaxis=dict(title="Total Revenue ($)", tickprefix="$", showgrid=True,
                        gridcolor="#F0F2F5"),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_top, use_container_width=True)
            export_csv_button(top_df, "top_customers.csv")

        # ── By Country ─────────────────────────────────────────────────────────────
        with col_right:
            st.markdown(
                "<strong style='font-size:0.95rem;color:#1B2A4A'>Customer by Country</strong><br>"
                "<span style='font-size:0.78rem;color:#6B7A8D'>Top 15 countries by number of customers</span>",
                unsafe_allow_html=True,
            )

            fig_country = go.Figure(go.Bar(
                x=country_df["customer_count"],
                y=country_df["country"],
                orientation="h",
                marker=dict(
                    color=country_df["customer_count"],
                    colorscale=[[0, "#D4DCF0"], [1, COLORS["primary"]]],
                    showscale=False,
                ),
                text=country_df["customer_count"],
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Customers: %{x}<br>"
                    "Revenue: $%{customdata:,.2f}"
                    "<extra></extra>"
                ),
                customdata=country_df["country_revenue"],
            ))
            fig_country.update_layout(
                height=380, margin=dict(l=10, r=40, t=10, b=10),
                xaxis=dict(title="Number of Customers", showgrid=True, gridcolor="#F0F2F5"),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_country, use_container_width=True)
            export_csv_button(country_df, "customers_by_country.csv")
        
            st.markdown("<br><br>", unsafe_allow_html=True)

        section_header("CUSTOMER RENTAL BEHAVIOR", "Genre Popularity & Revenue Correlation")

        with st.spinner("Loading behavior data…"):
            genre_df  = get_genre_popularity()
            scatter_df = get_rentals_vs_revenue()

        col_left, col_right = st.columns(2, gap="large")

        # ── Genre popularity ──────────────────────────────────────────────────────
        with col_left:
            st.markdown(
                "<strong style='font-size:0.95rem;color:#1B2A4A'>Favorite Genres</strong><br>"
                "<span style='font-size:0.78rem;color:#6B7A8D'>What kind of films do customers love to rent?</span>",
                unsafe_allow_html=True,
            )

            # Gradient color by rank
            n = len(genre_df)
            bar_colors = [
                f"rgba(208,92,120,{1 - i/n * 0.6})" for i in range(n)
            ]

            fig_genre = go.Figure(go.Bar(
                x=genre_df["total_rentals"],
                y=genre_df["genre"],
                orientation="h",
                marker_color=bar_colors,
                text=genre_df["total_rentals"],
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Rentals: %{x:,}<br>"
                    "Revenue: $%{customdata[0]:,.2f}<br>"
                    "Share: %{customdata[1]:.1f}%"
                    "<extra></extra>"
                ),
                customdata=genre_df[["total_revenue", "rental_share_pct"]].values,
            ))
            fig_genre.update_layout(
                height=440, margin=dict(l=10, r=50, t=10, b=10),
                xaxis=dict(title="Total Rentals", showgrid=True, gridcolor="#F0F2F5"),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_genre, use_container_width=True)
            export_csv_button(genre_df, "genre_popularity.csv")

        # ── Rentals vs Revenue scatter ─────────────────────────────────────────────
        with col_right:
            corr = get_correlation()
            st.markdown(
                "<strong style='font-size:0.95rem;color:#1B2A4A'>More Rentals = More Revenue</strong><br>"
                f"<span style='font-size:0.78rem;color:#6B7A8D'>"
                f"Each dot = 1 customer - dashed line shows the trend "
                f"(r = <strong>{corr:.2f}</strong>)</span>",
                unsafe_allow_html=True,
            )

            fig_scatter = go.Figure()

            for tier, color in SPENDING_TIER_COLORS.items():
                subset = scatter_df[scatter_df["spending_tier"] == tier]
                fig_scatter.add_trace(go.Scatter(
                    x=subset["rental_count"],
                    y=subset["total_revenue"],
                    mode="markers",
                    name=tier,
                    marker=dict(color=color, size=7, opacity=0.75,
                                line=dict(width=0.5, color="white")),
                    hovertemplate=(
                        "<b>%{customdata}</b><br>"
                        "Rentals: %{x}<br>"
                        "Revenue: $%{y:,.2f}"
                        "<extra></extra>"
                    ),
                    customdata=subset["customer_name"],
                ))

            # Regression trendline
            if not scatter_df.empty:
                x_vals = scatter_df["rental_count"].values
                y_vals = scatter_df["total_revenue"].values
                slope, intercept, *_ = stats.linregress(x_vals, y_vals)
                x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                y_line = slope * x_line + intercept
                fig_scatter.add_trace(go.Scatter(
                    x=x_line, y=y_line,
                    mode="lines",
                    name="Trend",
                    line=dict(color=COLORS["accent"], width=2, dash="dash"),
                    hoverinfo="skip",
                ))

            fig_scatter.update_layout(
                height=440, margin=dict(l=60, r=20, t=10, b=40),
                xaxis=dict(title="Number of Rentals", showgrid=True, gridcolor="#F0F2F5"),
                yaxis=dict(title="Total Revenue ($)", tickprefix="$",
                        showgrid=True, gridcolor="#F0F2F5"),
                legend=dict(orientation="v", x=1.01),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab2:
        # ── K-Means Clustering (ML) ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("ML CLUSTERING", "K-Means Customer Clusters on RFM Space")
        
        with st.spinner("Computing RFM segments…"):
            rfm_df = get_rfm_data()

        if rfm_df.empty:
            st.warning("No RFM data.")
            return
        
        st.markdown(
            '<span class="ml-badge">scikit-learn</span>'
            "<span style='font-size:0.82rem;color:#6B7A8D;margin-left:0.5rem;'>"
            "Unsupervised K-Means (k=4) - data-driven complement to rule-based RFM scoring</span>",
            unsafe_allow_html=True,
        )

        with st.spinner("Training K-Means model…"):
            labeled_df, model_info = fit_clusters(rfm_df)
            summary_df = cluster_summary(labeled_df)

        col5, col6 = st.columns([7, 3], gap="large")
        with col5:
            cluster_colors = {
                "Champions": SEGMENT_COLORS["Champions"],
                "Loyal Customers": SEGMENT_COLORS["Loyal Customers"],
                "Potential Loyalists": SEGMENT_COLORS["Potential Loyalists"],
                "Lost Customers": SEGMENT_COLORS["Lost Customers"],
            }
            fig_cl = go.Figure()
            for label, color in cluster_colors.items():
                sub = labeled_df[labeled_df["cluster_label"] == label]
                fig_cl.add_trace(go.Scatter(
                    x=sub["frequency"], y=sub["monetary"],
                    mode="markers",
                    name=label,
                    marker=dict(color=color, size=7, opacity=0.7),
                    hovertemplate="<b>%{customdata}</b><br>F: %{x} | M: $%{y:.2f}<extra></extra>",
                    customdata=sub["customer_name"],
                ))
            fig_cl.update_layout(
                height=360, margin=dict(l=60,r=20,t=30,b=40),
                title=dict(text="Frequency vs Monetary by Cluster",
                        font=dict(size=14, color=COLORS["primary"])),
                xaxis=dict(title="Frequency (rentals)", showgrid=True, gridcolor="#F0F2F5"),
                yaxis=dict(title="Monetary ($)", tickprefix="$", showgrid=True, gridcolor="#F0F2F5"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_cl, use_container_width=True)

        with col6:
            st.markdown(f"""
            <div style="background:#EEF2FF;border-radius:8px;padding:0.75rem 1rem;
                        margin-top:0.5rem;font-size:0.8rem;color:#1B2A4A;">
                <strong>Model Quality</strong><br>
                Silhouette Score: <strong>{model_info['silhouette_score']}</strong>
                (>0.3 indicates meaningful separation)<br>
                Inertia: {model_info['inertia']:,.0f}
            </div>
            """, unsafe_allow_html=True)

        # ── RFM Segmentation ──────────────────────────────────────────────────────
        section_header("RFM SEGMENTATION", "Customer Segmentation by Recency, Frequency & Monetary")
        st.markdown(
            "<p style='color:#6B7A8D;font-size:0.85rem;margin-top:-0.5rem;margin-bottom:1rem;'>"
            "Based on Recency, Frequency, Monetary - who is the best customer?</p>",
            unsafe_allow_html=True,
        )

        # Use K-Means cluster labels (from `labeled_df`) for segmentation visuals
        seg_counts = labeled_df["cluster_label"].value_counts().reset_index()
        seg_counts.columns = ["segment", "count"]
        seg_avg = labeled_df.groupby("cluster_label")["monetary"].mean().reset_index()
        seg_avg.columns = ["segment", "avg_spending"]

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("<strong style='font-size:0.9rem;color:#1B2A4A'>Segment Distribution</strong><br>"
                        "<span style='font-size:0.78rem;color:#6B7A8D'>Customer proportion per RFM segment</span>",
                        unsafe_allow_html=True)
            fig_pie = go.Figure(go.Pie(
                labels=seg_counts["segment"],
                values=seg_counts["count"],
                hole=0.55,
                marker=dict(colors=[SEGMENT_COLORS.get(s, "#ccc") for s in seg_counts["segment"]]),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>%{value} customers<extra></extra>",
            ))
            total = seg_counts["count"].sum()
            fig_pie.add_annotation(text=f"<b>{total}</b><br>customers",
                                x=0.5, y=0.5, showarrow=False,
                                font=dict(size=14, color=COLORS["primary"]))
            fig_pie.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10),
                                showlegend=True, paper_bgcolor="white")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.markdown("<strong style='font-size:0.9rem;color:#1B2A4A'>Avg Spending per Segment</strong><br>"
                        "<span style='font-size:0.78rem;color:#6B7A8D'>Champions and loyal customers make the biggest contribution</span>",
                        unsafe_allow_html=True)
            fig_bar = go.Figure(go.Bar(
                x=seg_avg["segment"],
                y=seg_avg["avg_spending"],
                marker_color=[SEGMENT_COLORS.get(s, "#ccc") for s in seg_avg["segment"]],
                text=seg_avg["avg_spending"].map("${:.2f}".format),
                textposition="outside",
            ))
            fig_bar.update_layout(
                height=320, margin=dict(l=10,r=10,t=10,b=10),
                xaxis=dict(title="Customer Segment"),
                yaxis=dict(title="Avg Spending ($)", tickprefix="$"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Segment count mini-cards
        st.markdown("<br>", unsafe_allow_html=True)
        seg_cols = st.columns(len(seg_counts))
        for col, (_, row) in zip(seg_cols, seg_counts.iterrows()):
            with col:
                color = SEGMENT_COLORS.get(row["segment"], "#ccc")
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:0.9rem;
                            box-shadow:0 2px 12px rgba(27,42,74,0.07);
                            border-top:3px solid {color};">
                    <div style="font-size:0.65rem;text-transform:uppercase;
                                letter-spacing:0.1em;color:#6B7A8D;font-weight:600;">
                        {row['segment']}
                    </div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.5rem;color:#1B2A4A;">
                        {row['count']}
                    </div>
                    <div style="font-size:0.72rem;color:{color};">● customers</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        segment_options = ["All"] + seg_counts["segment"].tolist()
        col_left, col_right = st.columns([8, 2], gap="medium")

        with col_right:
            selected_segment = st.selectbox(
                "Filter RFM export by segment",
                segment_options,
            )

        filtered_rfm_df = (
            labeled_df if selected_segment == "All"
            else labeled_df[labeled_df["cluster_label"] == selected_segment]
        )

        display_rfm_df = filtered_rfm_df.drop(columns=["cluster_id"], errors="ignore")

        with col_left:
            with st.expander(f"Full RFM Table ({selected_segment})"):
                st.dataframe(display_rfm_df, use_container_width=True, hide_index=True, column_config={
                    "customer_id": "Customer ID",
                    "customer_name": "Customer Name",
                    "email": "Email",
                    "recency_days": "Recency (days)",
                    "frequency": "Frequency",
                    "monetary": "Monetary ($)",
                    "r_score": "R Score",
                    "f_score": "F Score",
                    "m_score": "M Score",
                    "segment": "Segment",
                    "cluster_label": "Cluster Label"
                },
                )
                export_csv_button(
                    filtered_rfm_df,
                    f"rfm_segmentation_{selected_segment.lower().replace(' ', '_')}.csv",
                    label=("⬇ Download All RFM CSV" if selected_segment == "All"
                           else f"⬇ Download {selected_segment} RFM CSV")
                )

        # ── Spending Tier Analysis ─────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("SPENDING TIER ANALYSIS", "Revenue Contribution by Spending Quartile")

        with st.spinner("Loading spending tier data…"):
            tier_df = get_spending_tiers()

        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.markdown("<strong style='font-size:0.9rem;color:#1B2A4A'>Customer Count per Spending Tier</strong><br>"
                        "<span style='font-size:0.78rem;color:#6B7A8D'>Customer distribution based on spending tiers</span>",
                        unsafe_allow_html=True)
            fig_tier_pie = go.Figure(go.Pie(
                labels=tier_df["tier"],
                values=tier_df["customer_count"],
                hole=0.55,
                marker=dict(colors=[SPENDING_TIER_COLORS.get(t,"#ccc") for t in tier_df["tier"]]),
                textinfo="label+percent",
            ))
            total_t = tier_df["customer_count"].sum()
            fig_tier_pie.add_annotation(text=f"<b>{total_t}</b><br>customers",
                                        x=0.5, y=0.5, showarrow=False,
                                        font=dict(size=14, color=COLORS["primary"]))
            fig_tier_pie.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10),
                                        paper_bgcolor="white")
            st.plotly_chart(fig_tier_pie, use_container_width=True)

        with col4:
            st.markdown("<strong style='font-size:0.9rem;color:#1B2A4A'>Revenue Contribution by Spending Tier</strong><br>"
                        "<span style='font-size:0.78rem;color:#6B7A8D'>Which tier actually drives the most revenue?</span>",
                        unsafe_allow_html=True)
            fig_tier_bar = go.Figure(go.Bar(
                x=tier_df["tier"],
                y=tier_df["tier_revenue"],
                marker_color=[SPENDING_TIER_COLORS.get(t,"#ccc") for t in tier_df["tier"]],
                text=tier_df.apply(lambda r: f"${r['tier_revenue']:,.0f} ({r['revenue_pct']}%)", axis=1),
                textposition="outside",
            ))
            fig_tier_bar.update_layout(
                height=300, margin=dict(l=10,r=10,t=10,b=10),
                xaxis=dict(title="Spending Tier"),
                yaxis=dict(title="Total Revenue ($)", tickprefix="$"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_tier_bar, use_container_width=True)



def _top10_share(top_df) -> str:
    """Compute what % of total revenue the top 10 represent."""
    from analytics.kpi import get_kpis
    kpis = get_kpis()
    total = kpis.get("total_revenue", 1)
    share = top_df["total_spent"].sum() / total * 100
    return f"{share:.1f}"
