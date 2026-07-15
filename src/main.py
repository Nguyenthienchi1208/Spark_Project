from pyspark.sql import SparkSession

from config.settings import KAFKA_CONFIG, CHECKPOINT_PATH, logger
from read_stream import get_kafka_stream, transform_stream
from utils.postgres_handler import write_to_postgres, read_from_postgres
from utils.surrogate_keys import (
    customer_sk_expr,
    product_sk_expr,
    store_sk_expr,
    location_sk_expr,
    normalize_unix_timestamp,
)

from transforms.dim.dim_customer import transform_to_dim_customer
from transforms.dim.dim_product import transform_to_dim_product
from transforms.dim.dim_store import transform_to_dim_store
from transforms.dim.dim_location import process_dim_location as transform_to_dim_location
from transforms.dim.dim_date import transform_to_dim_date
from transforms.fact.fact_product_view import transform_to_fact_product_view

COLUMNS_MAPPING = {
    "dim_customer": ["customer_sk", "user_id_db", "email_address", "device_id", "user_agent", "resolution"],
    "dim_product": ["product_sk", "product_id", "collection", "alloy", "diamond"],
    "dim_store": ["store_sk", "store_id"],
    "dim_location": ["location_sk", "ip", "country", "region", "city", "latitude", "longitude"],
    "dim_date": ["date_sk", "full_date", "year", "month", "day", "quarter"],
    "fact_product_view": [
        "event_id", "user_id_db", "product_id", "store_id", "time_stamp",
        "date_sk", "customer_sk", "product_sk", "store_sk", "location_sk",
        "referrer_url", "current_url", "domain", "country_domain", "browser", "os",
    ],
}


def _is_empty(df):
    return df.limit(1).count() == 0


def _upsert_dim(spark, df, table_name, sk_col, columns):
    """Append only rows whose surrogate key is not already in Postgres."""
    if df is None or _is_empty(df):
        logger.info(f"Skip {table_name}: empty")
        return

    mapped = df.select(*[c for c in columns if c in df.columns]).dropDuplicates([sk_col])
    if _is_empty(mapped):
        return

    try:
        existing = read_from_postgres(spark, f"SELECT {sk_col} FROM {table_name}")
        new_rows = mapped.join(existing, sk_col, "left_anti")
    except Exception as e:
        logger.warning(f"Could not read existing keys from {table_name}: {e}. Writing full batch.")
        new_rows = mapped

    if _is_empty(new_rows):
        logger.info(f"Skip {table_name}: no new keys")
        return

    write_to_postgres(new_rows, table_name, mode="append")


def process_batch(df, batch_id):
    # Checkpoint can restore shuffle.partitions=200 — clamp every batch
    spark = SparkSession.getActiveSession()
    spark.conf.set("spark.sql.shuffle.partitions", "4")

    if _is_empty(df):
        logger.info(f"Batch {batch_id}: empty, skip")
        return

    row_count = df.count()
    logger.info(f"Processing batch: {batch_id} ({row_count} rows)")

    try:
        df_enriched = (
            df
            .withColumn("customer_sk", customer_sk_expr())
            .withColumn("product_sk", product_sk_expr(df.columns))
            .withColumn("store_sk", store_sk_expr())
            .withColumn("location_sk", location_sk_expr())
            .withColumn("time_stamp", normalize_unix_timestamp("time_stamp"))
            .cache()
        )
        # Materialize once so later dims/fact share work
        _ = df_enriched.count()

        logger.info(f"Batch {batch_id}: building dims")
        df_cust = transform_to_dim_customer(df_enriched)
        df_prod = transform_to_dim_product(df_enriched)
        df_store = transform_to_dim_store(df_enriched)
        df_loc = transform_to_dim_location(df_enriched)
        df_date = transform_to_dim_date(df_enriched)

        logger.info(f"Batch {batch_id}: upserting dims")
        _upsert_dim(spark, df_cust, "dim_customer", "customer_sk", COLUMNS_MAPPING["dim_customer"])
        _upsert_dim(spark, df_prod, "dim_product", "product_sk", COLUMNS_MAPPING["dim_product"])
        _upsert_dim(spark, df_store, "dim_store", "store_sk", COLUMNS_MAPPING["dim_store"])
        _upsert_dim(spark, df_loc, "dim_location", "location_sk", COLUMNS_MAPPING["dim_location"])
        _upsert_dim(spark, df_date, "dim_date", "date_sk", COLUMNS_MAPPING["dim_date"])

        logger.info(f"Batch {batch_id}: writing fact")
        df_fact = transform_to_fact_product_view(
            df_enriched, df_cust, df_prod, df_store, df_loc, df_date
        )
        fact_cols = [c for c in COLUMNS_MAPPING["fact_product_view"] if c in df_fact.columns]
        write_to_postgres(df_fact.select(*fact_cols), "fact_product_view", mode="append")

        df_enriched.unpersist()
        logger.info(f"Batch {batch_id} completed.")

    except Exception as e:
        logger.error(f"Batch {batch_id} failed: {str(e)}")
        raise e


def main():
    spark = (
        SparkSession.builder
        .appName("GlamiraStreamingPipeline")
        .config("spark.driver.memory", "1g")
        .config("spark.executor.memory", "1g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    raw_df = get_kafka_stream(spark, KAFKA_CONFIG)
    df_transformed = transform_stream(raw_df)

    query = (
        df_transformed.writeStream
        .foreachBatch(process_batch)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
