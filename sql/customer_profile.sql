-- sql/customer_profile.sql
-- Used by the Individual Customer Profiling page.
-- Parameterised with :customer_id.
-- Three separate queries for:
--   1. header stats
--   2. rental activity over time (monthly)
--   3. favorite genres

-- ── 1. Header stats ──────────────────────────────────────────────────────────
-- customer_profile_stats
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name      AS customer_name,
    c.email,
    co.country,
    COUNT(DISTINCT r.rental_id)              AS total_rentals,
    ROUND(SUM(p.amount)::NUMERIC, 2)         AS total_spent,
    ROUND(AVG(p.amount)::NUMERIC, 2)         AS avg_transaction,
    MIN(r.rental_date)::DATE                 AS first_rental,
    MAX(r.rental_date)::DATE                 AS last_rental,
    CASE WHEN c.activebool THEN 'Active' ELSE 'Inactive' END AS status
FROM customer  c
JOIN rental    r  ON c.customer_id = r.customer_id
JOIN payment   p  ON r.rental_id   = p.rental_id
JOIN address   a  ON c.address_id  = a.address_id
JOIN city      ci ON a.city_id     = ci.city_id
JOIN country   co ON ci.country_id = co.country_id
WHERE c.customer_id = :customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, co.country, c.activebool;

-- ── 2. Rental activity over time ─────────────────────────────────────────────
-- customer_profile_activity
SELECT
    DATE_TRUNC('month', r.rental_date)::DATE AS month,
    COUNT(*)                                  AS rentals
FROM rental r
WHERE r.customer_id = :customer_id
GROUP BY 1
ORDER BY 1;

-- ── 3. Favorite genres ────────────────────────────────────────────────────────
-- customer_profile_genres
SELECT
    cat.name                      AS genre,
    COUNT(DISTINCT r.rental_id)   AS rentals
FROM rental       r
JOIN inventory    i   ON r.inventory_id = i.inventory_id
JOIN film         f   ON i.film_id      = f.film_id
JOIN film_category fc ON f.film_id      = fc.film_id
JOIN category     cat ON fc.category_id = cat.category_id
WHERE r.customer_id = :customer_id
GROUP BY cat.name
ORDER BY rentals DESC;
