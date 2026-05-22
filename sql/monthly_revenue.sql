-- sql/monthly_revenue.sql
-- Monthly aggregation using DATE_TRUNC.
-- Includes MoM growth via LAG window function.
-- Used in the Revenue Trend dual-axis chart.

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
SELECT
    month,
    revenue,
    transactions,
    prev_revenue,
    mom_growth_pct
FROM with_growth
ORDER BY month;
