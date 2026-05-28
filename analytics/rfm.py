"""
analytics/rfm.py
RFM segmentation and spending tier quartile analysis.
"""
import pandas as pd
from database.connection import run_query

RFM_SQL = """
WITH raw_rfm AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name                              AS customer_name,
        c.email,
        CURRENT_DATE - MAX(p.payment_date)::DATE                        AS recency_days,
        COUNT(DISTINCT r.rental_id)                                     AS frequency,
        ROUND(SUM(p.amount)/COUNT(DISTINCT r.rental_id)::NUMERIC, 2)    AS monetary,
        ROUND(SUM(p.amount)::NUMERIC, 2)                                AS total_spent        
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email
),
-- Calculate RFM score thresholds based on the distribution of frequency and monetary values.
thresholds AS (
    SELECT
        -- Frequency Cutoffs (e.g., Median, 75th, and a strict 90th percentile for Peak)
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY frequency) AS f25,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY frequency) AS f50,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY frequency) AS f75,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY frequency) AS f90, -- Top 10%
        
        -- Monetary Cutoffs (Strict percentiles to isolate the highest-paying pink dots)
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY monetary)  AS m25,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY monetary)  AS m50,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY monetary)  AS m75,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY monetary)  AS m90  -- Top 10% (Peak LTV)
    FROM raw_rfm
),
scored AS (
    SELECT
        *,
        -- Fixed day boundaries ensure old transactions never get  5
        CASE 
            WHEN raw_rfm.recency_days <= 30  THEN 4
            WHEN raw_rfm.recency_days <= 90  THEN 3
            WHEN raw_rfm.recency_days <= 180 THEN 2
            ELSE 1 
        END AS r_score,
        
        -- Statistical Frequency scoring using thresholds
        CASE 
            WHEN raw_rfm.frequency >= thresholds.f90 THEN 4  -- Only your extreme power renters
            WHEN raw_rfm.frequency >= thresholds.f75 THEN 3
            WHEN raw_rfm.frequency >= thresholds.f50 THEN 2
            ELSE 1 
        END AS f_score,
        
        -- Statistical Monetary scoring using thresholds
        CASE 
            WHEN raw_rfm.monetary >= thresholds.m90 THEN 4   -- Limits '4' to only the peak of your LTV curve
            WHEN raw_rfm.monetary >= thresholds.m75 THEN 3
            WHEN raw_rfm.monetary >= thresholds.m50 THEN 2
            ELSE 1 
        END AS m_score
    FROM raw_rfm, thresholds
)
SELECT customer_id, customer_name, email,
       recency_days, frequency, monetary, total_spent,
       r_score, f_score, m_score
FROM scored
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
