-- sql/rfm_segmentation.sql
-- Full RFM pipeline:
--   1. compute raw R, F, M per customer
--   2. score each dimension into quartiles (NTILE 1-4, higher = better)
--   3. classify into business segments via CASE WHEN
-- Reference date is the MAX payment_date in the dataset (not CURRENT_DATE)
-- to keep results reproducible against the static DVD Rental snapshot.

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
        -- Recency: lower days = higher score → invert NTILE
        5 - NTILE(4) OVER (ORDER BY recency_days DESC) + 1 AS r_score,
        NTILE(4) OVER (ORDER BY frequency  ASC)            AS f_score,
        NTILE(4) OVER (ORDER BY monetary   ASC)            AS m_score
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
SELECT
    customer_id,
    customer_name,
    email,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    segment
FROM segmented
ORDER BY monetary DESC;
