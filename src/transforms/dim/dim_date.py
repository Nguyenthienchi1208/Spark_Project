from pyspark.sql import functions as F
from pyspark.sql.types import LongType
from utils.surrogate_keys import date_sk_expr


def transform_to_dim_date(df):
    """
    Build date dimension from an already-normalized Timestamp `time_stamp`.
    """
    if "time_stamp" not in df.columns:
        return df.filter(F.lit(False))

    df = (
        df.withColumn("date_ts", F.col("time_stamp").cast("timestamp"))
        .filter(F.col("date_ts").isNotNull())
    )

    df = (
        df.withColumn("year", F.year("date_ts"))
        .withColumn("month", F.month("date_ts"))
        .withColumn("day", F.dayofmonth("date_ts"))
        .withColumn("quarter", F.quarter("date_ts"))
        .withColumn("date_sk", date_sk_expr("date_ts"))
    )

    return (
        df.withColumn("full_date", F.to_date("date_ts"))
        .select("date_sk", "full_date", "year", "month", "day", "quarter")
        .dropDuplicates(["date_sk"])
    )
