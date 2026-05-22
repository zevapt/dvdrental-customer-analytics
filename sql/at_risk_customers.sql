-- sql/at_risk_customers.sql
-- Identifies customers who have not rented in 90+ days
-- relative to the latest rental date in the dataset.
-- Priority-scored by total spend descending.
-- Includes email for re-engagement campaigns.

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
    -- Risk score: higher spend + longer inactivity = higher priority to re-engage
    ROUND(
        (total_spent / NULLIF(days_inactive, 0)) * 100
    , 2)                                                AS risk_score,
    CASE
        WHEN days_inactive >= 150 THEN 'High'
        WHEN days_inactive >= 120 THEN 'Medium'
        ELSE 'Low'
    END                                                 AS churn_risk
FROM last_activity
WHERE days_inactive >= 90
ORDER BY total_spent DESC;
