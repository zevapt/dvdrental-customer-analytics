"""
analytics/insights.py
At-risk customer identification and dynamic insight text generation.
"""
import pandas as pd
from database.connection import run_query

AT_RISK_SQL = """
WITH reference_date AS (
    SELECT MAX(rental_date)::DATE AS ref_date FROM rental
),
last_activity AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name             AS customer_name,
        c.email,
        MAX(r.rental_date)::DATE                        AS last_rental_date,
        COUNT(DISTINCT r.rental_id)                     AS total_rentals,
        ROUND(SUM(p.amount)::NUMERIC, 2)                AS total_spent,
        (SELECT ref_date FROM reference_date)
            - MAX(r.rental_date)::DATE                  AS days_inactive
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    WHERE c.email IS NOT NULL
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email
)
SELECT
    customer_id,
    customer_name,
    email,
    last_rental_date,
    total_rentals,
    total_spent,
    days_inactive,
    ROUND((total_spent / NULLIF(days_inactive, 0)) * 100, 2) AS risk_score,
    CASE
        WHEN days_inactive >= 150 THEN 'High'
        WHEN days_inactive >= 120 THEN 'Medium'
        ELSE 'Low'
    END AS churn_risk
FROM last_activity
WHERE days_inactive >= 90
ORDER BY total_spent DESC
"""

CORRELATION_SQL = """
SELECT ROUND(CORR(rental_count, total_revenue)::NUMERIC, 4) AS correlation
FROM (
    SELECT
        COUNT(DISTINCT r.rental_id)             AS rental_count,
        ROUND(SUM(p.amount)::NUMERIC, 2)         AS total_revenue
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    GROUP BY c.customer_id
) t
"""

DURATION_STATS_SQL = """
SELECT
    ROUND(AVG(EXTRACT(DAY FROM (return_date - rental_date)))::NUMERIC, 1) AS avg_days,
    MODE() WITHIN GROUP (ORDER BY EXTRACT(DAY FROM (return_date - rental_date))::INT) AS mode_days
FROM rental
WHERE return_date IS NOT NULL
"""


def get_at_risk_customers() -> pd.DataFrame:
    return run_query(AT_RISK_SQL)


def get_correlation() -> float:
    df = run_query(CORRELATION_SQL)
    return float(df.iloc[0]["correlation"]) if not df.empty else 0.0


def get_duration_stats() -> dict:
    df = run_query(DURATION_STATS_SQL)
    if df.empty:
        return {"avg_days": 5.0, "mode_days": 7}
    row = df.iloc[0]
    return {"avg_days": float(row["avg_days"]), "mode_days": int(row["mode_days"])}


def generate_insights(scatter_df: pd.DataFrame, rfm_df: pd.DataFrame) -> list[dict]:
    """
    Dynamically generates executive insight cards based on current data.
    Returns a list of dicts with keys: title, metric, description, color.
    """
    insights = []

    # Revenue concentration
    if not scatter_df.empty:
        total_rev = scatter_df["total_revenue"].sum()
        n = len(scatter_df)
        top_20_pct = scatter_df.nlargest(max(1, int(n * 0.20)), "total_revenue")
        top_20_rev_pct = round(top_20_pct["total_revenue"].sum() / total_rev * 100, 1)
        insights.append({
            "title":       "Revenue Concentration",
            "metric":      f"{top_20_rev_pct}%",
            "description": f"of total revenue comes from the top 20% of customers - "
                           f"a small group of high-value customers drives most of the business.",
            "color":       "#D05C78",
        })

    # Correlation
    corr = get_correlation()
    insights.append({
        "title":       "Frequency Drives Revenue",
        "metric":      f"r = {corr:.2f}",
        "description": "correlation between rental frequency and revenue. "
                       "The more a customer rents, the more they spend - confirmed by the scatter trendline.",
        "color":       "#1B2A4A",
    })

    # Duration stats
    dur = get_duration_stats()
    insights.append({
        "title":       "Return Behavior",
        "metric":      f"{dur['mode_days']} days",
        "description": f"is the most common rental duration. Average is {dur['avg_days']} days. "
                       f"Fast returns support steady transaction flow and consistent revenue.",
        "color":       "#6B8DD6",
    })

    return insights
