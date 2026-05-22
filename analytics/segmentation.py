"""
analytics/segmentation.py
RFM segmentation and spending tier quartile analysis.
"""
import pandas as pd
from database.connection import run_query

RFM_SQL = """
WITH reference_date AS (
    SELECT MAX(payment_date)::DATE AS ref_date FROM payment
),
raw_rfm AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name                 AS customer_name,
        c.email,
        (SELECT ref_date FROM reference_date)
            - MAX(r.rental_date)::DATE                      AS recency_days,
        COUNT(DISTINCT r.rental_id)                         AS frequency,
        ROUND(SUM(p.amount)::NUMERIC, 2)                    AS monetary
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email
),
scored AS (
    SELECT
        *,
        5 - NTILE(4) OVER (ORDER BY recency_days DESC) + 1 AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC)              AS f_score,
        NTILE(4) OVER (ORDER BY monetary  ASC)              AS m_score
    FROM raw_rfm
),
segmented AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
                THEN 'Champions'
            WHEN r_score >= 2 AND f_score >= 3 AND m_score >= 3
                THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score <= 3
                THEN 'Potential Loyalists'
            WHEN r_score BETWEEN 2 AND 3 AND f_score >= 2 AND m_score >= 2
                THEN 'At Risk'
            ELSE 'Lost Customers'
        END AS segment
    FROM scored
)
SELECT customer_id, customer_name, email,
       recency_days, frequency, monetary,
       r_score, f_score, m_score, segment
FROM segmented
ORDER BY monetary DESC
"""

SPENDING_TIER_SQL = """
WITH customer_spend AS (
    SELECT
        c.customer_id,
        ROUND(SUM(p.amount)::NUMERIC, 2) AS total_spent,
        COUNT(DISTINCT r.rental_id)       AS total_rentals
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    GROUP BY c.customer_id
),
tiered AS (
    SELECT
        *,
        CASE NTILE(4) OVER (ORDER BY total_spent ASC)
            WHEN 1 THEN 'Low Spender'
            WHEN 2 THEN 'Mid Spender'
            WHEN 3 THEN 'High Spender'
            WHEN 4 THEN 'Top Spender'
        END AS tier,
        NTILE(4) OVER (ORDER BY total_spent ASC) AS tier_num
    FROM customer_spend
)
SELECT
    tier,
    tier_num,
    COUNT(*)                                              AS customer_count,
    ROUND(SUM(total_spent)::NUMERIC, 2)                   AS tier_revenue,
    ROUND(AVG(total_spent)::NUMERIC, 2)                   AS avg_spend,
    ROUND(MIN(total_spent)::NUMERIC, 2)                   AS min_spend,
    ROUND(MAX(total_spent)::NUMERIC, 2)                   AS max_spend,
    ROUND(SUM(total_spent)::NUMERIC / SUM(SUM(total_spent)) OVER () * 100, 1) AS revenue_pct
FROM tiered
GROUP BY tier, tier_num
ORDER BY tier_num
"""


def get_rfm_data() -> pd.DataFrame:
    return run_query(RFM_SQL)


def get_spending_tiers() -> pd.DataFrame:
    return run_query(SPENDING_TIER_SQL)
