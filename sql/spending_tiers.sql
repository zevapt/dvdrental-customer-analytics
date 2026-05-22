-- sql/spending_tiers.sql
-- Divides the customer base into 4 equal quartiles by total spend.
-- Returns per-tier summary for revenue contribution analysis.

WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name     AS customer_name,
        ROUND(SUM(p.amount)::NUMERIC, 2)        AS total_spent,
        COUNT(DISTINCT r.rental_id)             AS total_rentals
    FROM customer  c
    JOIN rental    r ON c.customer_id = r.customer_id
    JOIN payment   p ON r.rental_id   = p.rental_id
    GROUP BY c.customer_id, c.first_name, c.last_name
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
    ROUND(
        SUM(total_spent)::NUMERIC
        / SUM(SUM(total_spent)) OVER () * 100
    , 1)                                                  AS revenue_pct
FROM tiered
GROUP BY tier, tier_num
ORDER BY tier_num;
