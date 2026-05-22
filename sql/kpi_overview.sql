-- sql/kpi_overview.sql
-- Five headline KPIs pulled in a single pass.
-- Returns one row with all metrics for the Hero Header section.

SELECT
    COUNT(DISTINCT c.customer_id)                          AS total_customers,
    ROUND(SUM(p.amount)::NUMERIC, 2)                       AS total_revenue,
    COUNT(DISTINCT r.rental_id)                            AS total_rentals,
    ROUND(AVG(p.amount)::NUMERIC, 2)                       AS avg_transaction_value,
    ROUND((SUM(p.amount) / COUNT(DISTINCT c.customer_id))::NUMERIC, 2) AS avg_clv
FROM customer c
JOIN rental  r ON c.customer_id = r.customer_id
JOIN payment p ON r.rental_id   = p.rental_id;
