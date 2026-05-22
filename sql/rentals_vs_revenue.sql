-- sql/rentals_vs_revenue.sql
-- Per-customer rental frequency vs total revenue.
-- Used for scatter plot with regression trendline.
-- Spending tier via NTILE(4) for color segmentation.

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
ORDER BY total_revenue DESC;
