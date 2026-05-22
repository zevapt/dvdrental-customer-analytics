"""
database/connection.py
SQLAlchemy engine factory, query runner, and connection health check.
All query execution flows through here so caching, error handling,
and pooling are managed in a single place.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

from config.settings import DATABASE_URL, CACHE_TTL


# ─── Engine singleton ─────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    """
    Returns a long-lived SQLAlchemy engine backed by a connection pool.
    Using QueuePool with conservative settings to avoid exhausting
    PostgreSQL's max_connections on shared instances.
    """
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=3,
        max_overflow=5,
        pool_pre_ping=True,        # validates connection before each use
        pool_recycle=1800,         # recycle connections every 30 minutes
        connect_args={"connect_timeout": 10},
    )
    return engine


# ─── Query runner ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """
    Execute a SQL string and return a DataFrame.
    Results are cached for CACHE_TTL seconds so repeated filter
    interactions don't re-hit the database on every widget change.

    Parameters
    ----------
    sql    : Raw SQL string (use :param_name placeholders for safety).
    params : Optional dict of bind parameters.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


# ─── Health check ─────────────────────────────────────────────────────────────
def check_connection() -> bool:
    """Returns True if the database is reachable."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
