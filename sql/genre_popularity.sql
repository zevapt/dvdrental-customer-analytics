-- sql/genre_popularity.sql
-- Genre rental count and revenue contribution.
-- Joins: rental → inventory → film → film_category → category
-- + payment for revenue.

SELECT
    cat.name                                AS genre,
    COUNT(DISTINCT r.rental_id)             AS total_rentals,
    ROUND(SUM(p.amount)::NUMERIC, 2)        AS total_revenue,
    ROUND(AVG(p.amount)::NUMERIC, 2)        AS avg_revenue_per_rental,
    ROUND(
        COUNT(DISTINCT r.rental_id)::NUMERIC
        / SUM(COUNT(DISTINCT r.rental_id)) OVER () * 100
    , 1)                                    AS rental_share_pct
FROM rental       r
JOIN inventory    i   ON r.inventory_id  = i.inventory_id
JOIN film         f   ON i.film_id       = f.film_id
JOIN film_category fc ON f.film_id       = fc.film_id
JOIN category     cat ON fc.category_id  = cat.category_id
JOIN payment      p   ON r.rental_id     = p.rental_id
GROUP BY cat.name
ORDER BY total_rentals DESC;
