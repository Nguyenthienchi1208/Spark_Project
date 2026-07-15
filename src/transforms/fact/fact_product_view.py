from pyspark.sql import functions as F
from utils.surrogate_keys import (
    date_sk_expr,
    customer_sk_expr,
    product_sk_expr,
    store_sk_expr,
    location_sk_expr,
    UNKNOWN_SK,
)
from utils.event_enrichment import enrich_event_attrs


def transform_to_fact_product_view(df_event, dim_customer, dim_product, dim_store, dim_location, dim_date):
    """
    Build fact rows with SKs plus reporting attributes:
    referrer_url, current_url, domain, country_domain, browser, os.
    """
    _ = (dim_customer, dim_product, dim_store, dim_location, dim_date)

    fact_df = enrich_event_attrs(df_event)

    fact_df = (
        fact_df
        .withColumn("customer_sk", customer_sk_expr())
        .withColumn("product_sk", product_sk_expr(fact_df.columns))
        .withColumn("store_sk", store_sk_expr())
        .withColumn("location_sk", location_sk_expr())
        .withColumn("date_sk", date_sk_expr("time_stamp"))
    )

    for sk_col in ("customer_sk", "product_sk", "store_sk", "location_sk"):
        fact_df = fact_df.withColumn(sk_col, F.coalesce(F.col(sk_col), F.lit(UNKNOWN_SK)))

    return fact_df
