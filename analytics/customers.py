"""
analytics/customers.py
Top customers and geographic distribution queries.
"""
import pandas as pd
from database.connection import run_query

TOP_CUSTOMERS_SQL = """
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name                      AS customer_name,
    c.email,
    co.country,
    ROUND(SUM(p.amount)::NUMERIC, 2)                         AS total_spent,
    COUNT(DISTINCT r.rental_id)                              AS total_rentals,
    ROUND(AVG(p.amount)::NUMERIC, 2)                         AS avg_transaction,
    DENSE_RANK() OVER (ORDER BY SUM(p.amount) DESC)          AS spend_rank
FROM customer  c
JOIN rental    r  ON c.customer_id = r.customer_id
JOIN payment   p  ON r.rental_id   = p.rental_id
JOIN address   a  ON c.address_id  = a.address_id
JOIN city      ci ON a.city_id     = ci.city_id
JOIN country   co ON ci.country_id = co.country_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, co.country
ORDER BY total_spent DESC
LIMIT 10
"""

BY_COUNTRY_SQL = """
SELECT
    co.country,
    COUNT(DISTINCT c.customer_id)    AS customer_count,
    ROUND(SUM(p.amount)::NUMERIC, 2) AS country_revenue
FROM customer  c
JOIN rental    r  ON c.customer_id = r.customer_id
JOIN payment   p  ON r.rental_id   = p.rental_id
JOIN address   a  ON c.address_id  = a.address_id
JOIN city      ci ON a.city_id     = ci.city_id
JOIN country   co ON ci.country_id = co.country_id
GROUP BY co.country
ORDER BY customer_count DESC
LIMIT 15
"""

ALL_CUSTOMERS_SQL = """
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    c.activebool
FROM customer c
ORDER BY c.last_name, c.first_name
"""


def get_top_customers() -> pd.DataFrame:
    return run_query(TOP_CUSTOMERS_SQL)


def get_customers_by_country() -> pd.DataFrame:
    return run_query(BY_COUNTRY_SQL)


def get_all_customers() -> pd.DataFrame:
    return run_query(ALL_CUSTOMERS_SQL)
