-- sql/customer_by_country.sql
-- Customer distribution across countries via 4-table join.
-- Used for geographic distribution bar chart.

SELECT
    co.country,
    COUNT(DISTINCT c.customer_id)   AS customer_count,
    ROUND(SUM(p.amount)::NUMERIC, 2) AS country_revenue,
    ROUND(AVG(p.amount)::NUMERIC, 2) AS avg_spend_per_payment
FROM customer  c
JOIN rental    r  ON c.customer_id = r.customer_id
JOIN payment   p  ON r.rental_id   = p.rental_id
JOIN address   a  ON c.address_id  = a.address_id
JOIN city      ci ON a.city_id     = ci.city_id
JOIN country   co ON ci.country_id = co.country_id
GROUP BY co.country
ORDER BY customer_count DESC
LIMIT 15;
