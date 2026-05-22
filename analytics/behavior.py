"""
analytics/behavior.py
Genre popularity and rental-vs-revenue per customer.
"""
import pandas as pd
from database.connection import run_query

GENRE_SQL = """
SELECT
    cat.name                                AS genre,
    COUNT(DISTINCT r.rental_id)             AS total_rentals,
    ROUND(SUM(p.amount)::NUMERIC, 2)        AS total_revenue,
    ROUND(AVG(p.amount)::NUMERIC, 2)        AS avg_revenue_per_rental,
    ROUND(
        COUNT(DISTINCT r.rental_id)::NUMERIC
        / SUM(COUNT(DISTINCT r.rental_id)) OVER () * 100
    , 1)                                    AS rental_share_pct
FROM rental       r
JOIN inventory    i   ON r.inventory_id  = i.inventory_id
JOIN film         f   ON i.film_id       = f.film_id
JOIN film_category fc ON f.film_id       = fc.film_id
JOIN category     cat ON fc.category_id  = cat.category_id
JOIN payment      p   ON r.rental_id     = p.rental_id
GROUP BY cat.name
ORDER BY total_rentals DESC
"""

SCATTER_SQL = """
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name             AS customer_name,
        COUNT(DISTINCT r.rental_id)                     AS rental_count,
        ROUND(SUM(p.amount)::NUMERIC, 2)                AS total_revenue,
        ROUND(AVG(p.amount)::NUMERIC, 2)                AS avg_transaction
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    GROUP BY c.customer_id, c.first_name, c.last_name
)
SELECT
    customer_id,
    customer_name,
    rental_count,
    total_revenue,
    avg_transaction,
    CASE NTILE(4) OVER (ORDER BY total_revenue)
        WHEN 1 THEN 'Low Spender'
        WHEN 2 THEN 'Mid Spender'
        WHEN 3 THEN 'High Spender'
        WHEN 4 THEN 'Top Spender'
    END AS spending_tier
FROM customer_metrics
ORDER BY total_revenue DESC
"""

DURATION_SQL = """
SELECT
    EXTRACT(DAY FROM (return_date - rental_date))::INT AS rental_duration_days,
    COUNT(*)                                            AS count
FROM rental
WHERE return_date IS NOT NULL
GROUP BY 1
ORDER BY 1
"""


def get_genre_popularity() -> pd.DataFrame:
    return run_query(GENRE_SQL)


def get_rentals_vs_revenue() -> pd.DataFrame:
    return run_query(SCATTER_SQL)


def get_rental_duration() -> pd.DataFrame:
    return run_query(DURATION_SQL)
