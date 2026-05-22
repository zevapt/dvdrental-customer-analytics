# Customer Behavior & Revenue Analytics Dashboard

> **BI & Analytics Engineering portfolio project**  
> Built on the PostgreSQL DVD Rental database · Python · Streamlit · Plotly · scikit-learn

![Python](https://img.shields.io/badge/Python-3.11-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)

---

## Overview

This project transforms raw DVD rental transactional data into a fully interactive analytics dashboard covering customer behaviour, RFM segmentation, churn detection, revenue optimisation, machine learning clustering, and individual customer profiling - all backed by a live PostgreSQL connection and fully containerized using Docker for consistent local development and deployment.

---

## Tech Stack

| Layer            | Technology                                    |
|------------------|-----------------------------------------------|
| Database         | PostgreSQL 15+ · dvdrental schema             |
| ORM / Driver     | SQLAlchemy 2.0 · psycopg2-binary              |
| Data Layer       | Pandas 2.x                                    |
| Dashboard        | Streamlit 1.35                                |
| Visualisation    | Plotly 5.x                                    |
| ML               | scikit-learn 1.5 · scipy                      |
| Styling          | Custom CSS injected via `st.markdown`         |
| Containerization | Docker · Docker Compose                     |

---

## Project Structure

```
dvd-rental-analytics/
├── app.py                          # Streamlit entry point + sidebar nav
├── requirements.txt
├── Dockerfile                      # Streamlit application container
├── docker-compose.yml              # Multi-container orchestration
├── .env.example                    # Copy to .env and fill credentials
│
├── config/
│   └── settings.py                 # DB URL, colour palette, thresholds
│
├── database/
│   └── connection.py               # SQLAlchemy engine, run_query(), health check
│
├── sql/                            # All SQL as standalone files (reusable)
│   ├── kpi_overview.sql
│   ├── monthly_revenue.sql
│   ├── top_customers.sql
│   ├── customer_by_country.sql
│   ├── genre_popularity.sql
│   ├── rentals_vs_revenue.sql
│   ├── rfm_segmentation.sql
│   ├── spending_tiers.sql
│   ├── at_risk_customers.sql
│   └── customer_profile.sql
│
├── analytics/                      # Business logic layer
│   ├── kpi.py
│   ├── revenue.py
│   ├── customers.py
│   ├── behavior.py
│   ├── segmentation.py
│   └── insights.py
│
├── ml/
│   └── clustering.py               # K-Means RFM clustering pipeline
│
├── dashboard/
│   ├── styles.py                   # Global CSS injection
│   ├── components.py               # Reusable UI components
│   └── pages/
│       ├── overview.py             # Hero + KPIs + Monthly revenue dual-axis chart
│       ├── customers.py            # Top 10 + by-country + Genre + scatter plot
│       ├── segmentation.py         # RFM + spending tiers + K-Means
│       ├── insights.py             # At-risk table + insight cards
│       └── customer_profile.py     # Individual customer deep-dive
│
└── utils/
    └── formatters.py               # Shared number/currency formatters
```

---

## Dashboard Pages and Tabs

| Page | Key Features |
|------|-------------|
| **Executive Overview** | KPI cards · Revenue trends · MoM growth · Peak annotations |
| **Customer Intelligence** | Top customers · Geographic distribution · Genre insights · Revenue correlation |
| **Segmentation & ML** | RFM segmentation · Spending tiers · K-Means clustering |
| **Strategic Insights** | At-risk customers · Retention opportunities · Dynamic insights |
| **Customer Profile** | Customer drill-down · Activity timeline · Genre & spending trends |

---

## SQL Techniques Demonstrated

- `DATE_TRUNC` monthly aggregation
- `LAG()` for MoM growth
- `NTILE(4)` spending quartiles
- `DENSE_RANK()` customer ranking
- `CORR()` Pearson correlation
- CTEs with `WITH` clauses
- `CASE WHEN` segmentation logic
- Window functions: `OVER (ORDER BY ... PARTITION BY ...)`
- Multi-table joins across 6+ tables

---

## Machine Learning

**Model:** K-Means clustering (k=3) on StandardScaler-normalised RFM features.

**Why K-Means + RFM?**  
RFM dimensions create a natural 3D customer value space. K-Means identifies
data-driven cluster boundaries without the manual threshold assumptions of
rule-based scoring. Silhouette score validates cluster quality.

**Output clusters:** Premium / Regular / Dormant -> each with actionable
retention strategies.

---

## Key Business Findings

- **Top 20% of customers generate ~27% of total revenue** (mild concentration)
- **Rental frequency ↔ revenue correlation r ≈ 0.88** (strong positive)
- **7-day mode rental duration** - fast returns enable inventory velocity
- **441 at-risk customers** (90d+ inactive) contactable via email - prime win-back pool
- **Top Spenders generate 2× the revenue** of Low Spenders per customer

---

## Future Scalability

| Idea | Technology |
|------|-----------|
| Cloud deployment | Streamlit Community Cloud / AWS ECS |
| Data pipeline orchestration | Apache Airflow / Prefect |
| Transformation layer | dbt (models replace raw SQL files) |
| CI/CD | GitHub Actions → test → deploy |
| Warehouse migration | Snowflake / BigQuery / Redshift |
| Real-time streaming | Kafka + Flink |
| A/B testing layer | Statsig / GrowthBook |
