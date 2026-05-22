"""
analytics/kpi.py
Loads headline KPI metrics from the database.
"""
from database.connection import run_query

KPI_SQL = """
SELECT
    COUNT(DISTINCT c.customer_id)                                              AS total_customers,
    ROUND(SUM(p.amount)::NUMERIC, 2)                                           AS total_revenue,
    COUNT(DISTINCT r.rental_id)                                                AS total_rentals,
    ROUND(AVG(p.amount)::NUMERIC, 2)                                           AS avg_transaction_value,
    ROUND((SUM(p.amount) / COUNT(DISTINCT c.customer_id))::NUMERIC, 2)        AS avg_clv
FROM customer c
JOIN rental   r ON c.customer_id = r.customer_id
JOIN payment  p ON r.rental_id   = p.rental_id
"""


def get_kpis() -> dict:
    """Returns a dict of the five headline KPI values."""
    df = run_query(KPI_SQL)
    if df.empty:
        return {}
    row = df.iloc[0]
    return {
        "total_customers":      int(row["total_customers"]),
        "total_revenue":        float(row["total_revenue"]),
        "total_rentals":        int(row["total_rentals"]),
        "avg_transaction_value": float(row["avg_transaction_value"]),
        "avg_clv":              float(row["avg_clv"]),
    }
