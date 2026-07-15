from pyspark.sql import functions as F
from utils.surrogate_keys import store_sk_expr, UNKNOWN_SK


def transform_to_dim_store(df):
    if "store_id" not in df.columns:
        return None

    dim_store = (
        df.select(F.col("store_id").cast("string").alias("store_id"))
        .filter(F.col("store_id").isNotNull() & (F.trim(F.col("store_id")) != "") & (F.lower(F.col("store_id")) != "none"))
        .dropDuplicates(["store_id"])
        .withColumn("store_sk", store_sk_expr().cast("string"))
        .filter(F.col("store_sk").isNotNull() & (F.col("store_sk") != UNKNOWN_SK))
    )

    return dim_store.select("store_sk", "store_id")
