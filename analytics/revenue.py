"""
analytics/revenue.py
Monthly revenue trend data including MoM growth.
"""
import pandas as pd
from database.connection import run_query

MONTHLY_SQL = """
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', p.payment_date)::DATE  AS month,
        ROUND(SUM(p.amount)::NUMERIC, 2)            AS revenue,
        COUNT(p.payment_id)                         AS transactions
    FROM payment p
    GROUP BY 1
),
with_growth AS (
    SELECT
        month,
        revenue,
        transactions,
        LAG(revenue) OVER (ORDER BY month)          AS prev_revenue,
        ROUND(
            (revenue - LAG(revenue) OVER (ORDER BY month))
            / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100
        , 1)                                        AS mom_growth_pct
    FROM monthly
)
SELECT month, revenue, transactions, prev_revenue, mom_growth_pct
FROM with_growth
ORDER BY month
"""


def get_monthly_revenue() -> pd.DataFrame:
    df = run_query(MONTHLY_SQL)
    df["month"] = pd.to_datetime(df["month"])
    df["month_label"] = df["month"].dt.strftime("%b %Y")
    return df
