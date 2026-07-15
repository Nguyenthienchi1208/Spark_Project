"""Shared surrogate-key and timestamp helpers used by enrich + all dims + fact."""

from pyspark.sql import Column
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType


UNKNOWN_SK = "-1"


def _blank_to_null(col_name: str) -> Column:
    """Treat null / empty / whitespace-only strings as missing."""
    c = F.col(col_name)
    return F.when(F.trim(c) == "", F.lit(None)).otherwise(c)


def customer_sk_expr() -> Column:
    """Deterministic customer key: prefer user_id_db, else device_id."""
    identity = F.coalesce(_blank_to_null("user_id_db"), _blank_to_null("device_id"))
    return F.when(identity.isNull(), F.lit(UNKNOWN_SK)).otherwise(
        F.sha2(F.concat_ws("_", identity), 256)
    )


def product_sk_expr(df_columns=None) -> Column:
    """Deterministic product key from the first available product id field."""
    candidates = ["product_id", "viewing_product_id", "recommendation_product_id"]
    available = []
    for name in candidates:
        if df_columns is None or name in df_columns:
            available.append(_blank_to_null(name))
    if not available:
        return F.lit(UNKNOWN_SK)
    pid = F.coalesce(*available)
    return F.when(pid.isNull(), F.lit(UNKNOWN_SK)).otherwise(
        F.sha2(F.concat_ws("_", pid), 256)
    )


def store_sk_expr() -> Column:
    store_id = _blank_to_null("store_id")
    return F.when(store_id.isNull(), F.lit(UNKNOWN_SK)).otherwise(
        F.sha2(F.concat_ws("_", store_id), 256)
    )


def location_sk_expr() -> Column:
    ip = _blank_to_null("ip")
    return F.when(ip.isNull(), F.lit(UNKNOWN_SK)).otherwise(
        F.sha2(F.concat_ws("_", ip), 256)
    )


def normalize_unix_timestamp(col_name: str = "time_stamp") -> Column:
    """
    Convert Unix epoch to Spark Timestamp.
    Values >= 1e12 are treated as milliseconds; otherwise as seconds.
    """
    raw = F.col(col_name).cast("long")
    seconds = F.when(raw >= F.lit(10**12), raw / 1000).otherwise(raw)
    return F.from_unixtime(seconds).cast(TimestampType())


def date_sk_expr(timestamp_col: str = "time_stamp") -> Column:
    return F.date_format(F.col(timestamp_col), "yyyyMMdd").cast("long")
