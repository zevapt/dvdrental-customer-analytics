"""
config/settings.py
Central configuration for the DVD Rental Analytics project.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Database ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "dvdrental"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

# ─── Caching ──────────────────────────────────────────────────────────────────
CACHE_TTL = 300  # seconds

# ─── Business thresholds ─────────────────────────────────────────────────────
CHURN_DAYS_THRESHOLD = 90
TOP_N_CUSTOMERS = 10
TOP_N_COUNTRIES = 15
RFM_SEGMENTS = {
    "Champions":         {"r": (4, 5), "f": (4, 5), "m": (4, 5)},
    "Loyal Customers":   {"r": (2, 5), "f": (3, 5), "m": (3, 5)},
    "Potential Loyalists":{"r": (3, 5), "f": (1, 3), "m": (1, 3)},
    "At Risk":           {"r": (2, 3), "f": (2, 5), "m": (2, 5)},
    "Lost Customers":    {"r": (1, 2), "f": (1, 2), "m": (1, 2)},
}

# ─── Color palette ────────────────────────────────────────────────────────────
COLORS = {
    "primary":    "#1B2A4A",
    "accent":     "#D05C78",
    "accent2":    "#6B8DD6",
    "neutral":    "#A8B4C8",
    "surface":    "#F5F7FA",
    "text":       "#1B2A4A",
    "champions":  "#D05C78",
    "loyal":      "#1B2A4A",
    "potential":  "#6B8DD6",
    "at_risk":    "#F0A500",
    "lost":       "#A8B4C8",
}

SPENDING_TIER_COLORS = {
    "Low Spender":     "#A8B4C8",
    "Mid Spender":     "#6B8DD6",
    "High Spender":    "#1B2A4A",
    "Top Spender":     "#D05C78",
}
