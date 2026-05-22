-- sql/top_customers.sql
-- Ranks customers by cumulative payment amount.
-- Includes rental count, avg transaction, and estimated CLV.

SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name                     AS customer_name,
    c.email,
    co.country,
    ROUND(SUM(p.amount)::NUMERIC, 2)                        AS total_spent,
    COUNT(DISTINCT r.rental_id)                             AS total_rentals,
    ROUND(AVG(p.amount)::NUMERIC, 2)                        AS avg_transaction,
    -- CLV proxy: annualised based on active months
    ROUND(
        SUM(p.amount)::NUMERIC
        / NULLIF(
            EXTRACT(MONTH FROM AGE(MAX(p.payment_date), MIN(p.payment_date))) + 1
          , 0) * 12
    , 2)                                                    AS estimated_clv,
    DENSE_RANK() OVER (ORDER BY SUM(p.amount) DESC)         AS spend_rank
FROM customer     c
JOIN rental       r  ON c.customer_id = r.customer_id
JOIN payment      p  ON r.rental_id   = p.rental_id
JOIN address      a  ON c.address_id  = a.address_id
JOIN city         ci ON a.city_id     = ci.city_id
JOIN country      co ON ci.country_id = co.country_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, co.country
ORDER BY total_spent DESC
LIMIT 10;
