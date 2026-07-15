"""Postgres helpers for the Glamira report dashboard."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@lru_cache(maxsize=1)
def get_engine():
    host = _env("POSTGRES_HOST", "localhost")
    port = _env("POSTGRES_PORT", "5433")
    user = _env("POSTGRES_USER", "postgres")
    password = _env("POSTGRES_PASSWORD", "UnigapPostgres@123")
    db = _env("POSTGRES_DB", "postgres")
    url = f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:{port}/{db}"
    return create_engine(url, pool_pre_ping=True, pool_size=3, max_overflow=2)


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def available_report_dates() -> list:
    df = run_query(
        """
        SELECT DISTINCT time_stamp::date AS report_date
        FROM fact_product_view
        WHERE time_stamp IS NOT NULL
        ORDER BY 1 DESC
        LIMIT 60
        """
    )
    return [d for d in df["report_date"].tolist() if d is not None]


def fetch_kpis(report_date) -> dict:
    row = run_query(
        """
        SELECT
            COUNT(*) AS views_today,
            COUNT(DISTINCT NULLIF(product_id, '')) AS products_today,
            COUNT(DISTINCT NULLIF(store_id, '')) AS stores_today,
            COUNT(DISTINCT country_domain) AS countries_today,
            MAX(time_stamp) AS last_event_at
        FROM fact_product_view
        WHERE time_stamp::date = :d
        """,
        {"d": report_date},
    ).iloc[0]
    return row.to_dict()


def top10_products_today(report_date) -> pd.DataFrame:
    return run_query(
        """
        SELECT
            product_id,
            COUNT(*) AS views
        FROM fact_product_view
        WHERE time_stamp::date = :d
          AND product_id IS NOT NULL
          AND TRIM(product_id) <> ''
          AND product_sk <> '-1'
        GROUP BY product_id
        ORDER BY views DESC
        LIMIT 10
        """,
        {"d": report_date},
    )


def top10_countries_today(report_date) -> pd.DataFrame:
    """Country from storefront domain (country_domain), not IP GeoIP."""
    return run_query(
        """
        SELECT
            COALESCE(NULLIF(country_domain, ''), 'Unknown') AS country,
            COUNT(*) AS views
        FROM fact_product_view
        WHERE time_stamp::date = :d
        GROUP BY 1
        ORDER BY views DESC
        LIMIT 10
        """,
        {"d": report_date},
    )


def top5_referrers_today(report_date) -> pd.DataFrame:
    return run_query(
        """
        SELECT
            COALESCE(NULLIF(TRIM(referrer_url), ''), '(direct / empty)') AS referrer_url,
            COUNT(*) AS views
        FROM fact_product_view
        WHERE time_stamp::date = :d
        GROUP BY 1
        ORDER BY views DESC
        LIMIT 5
        """,
        {"d": report_date},
    )


def stores_by_country(report_date, country: str) -> pd.DataFrame:
    return run_query(
        """
        SELECT
            COALESCE(NULLIF(store_id, ''), '(unknown)') AS store_id,
            COUNT(*) AS views
        FROM fact_product_view
        WHERE time_stamp::date = :d
          AND COALESCE(NULLIF(country_domain, ''), 'Unknown') = :country
        GROUP BY 1
        ORDER BY views DESC
        """,
        {"d": report_date, "country": country},
    )


def product_views_by_hour(report_date, product_id: str) -> pd.DataFrame:
    return run_query(
        """
        SELECT
            EXTRACT(HOUR FROM time_stamp)::int AS hour,
            COUNT(*) AS views
        FROM fact_product_view
        WHERE time_stamp::date = :d
          AND product_id = :product_id
        GROUP BY 1
        ORDER BY 1
        """,
        {"d": report_date, "product_id": product_id},
    )


def browser_os_views_by_hour(report_date) -> pd.DataFrame:
    return run_query(
        """
        SELECT
            EXTRACT(HOUR FROM time_stamp)::int AS hour,
            COALESCE(NULLIF(browser, ''), 'Unknown') AS browser,
            COALESCE(NULLIF(os, ''), 'Unknown') AS os,
            COUNT(*) AS views
        FROM fact_product_view
        WHERE time_stamp::date = :d
        GROUP BY 1, 2, 3
        ORDER BY 1, views DESC
        """,
        {"d": report_date},
    )


def list_countries(report_date) -> list[str]:
    df = run_query(
        """
        SELECT DISTINCT COALESCE(NULLIF(country_domain, ''), 'Unknown') AS country
        FROM fact_product_view
        WHERE time_stamp::date = :d
        ORDER BY 1
        """,
        {"d": report_date},
    )
    return df["country"].tolist()


def list_products(report_date, limit: int = 200) -> list[str]:
    df = run_query(
        """
        SELECT product_id
        FROM fact_product_view
        WHERE time_stamp::date = :d
          AND product_id IS NOT NULL
          AND TRIM(product_id) <> ''
        GROUP BY product_id
        ORDER BY COUNT(*) DESC
        LIMIT :limit
        """,
        {"d": report_date, "limit": limit},
    )
    return df["product_id"].tolist()
