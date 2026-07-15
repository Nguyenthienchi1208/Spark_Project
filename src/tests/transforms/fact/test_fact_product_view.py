import pytest
from pyspark.sql import SparkSession
from transforms.fact.fact_product_view import transform_to_fact_product_view
from utils.surrogate_keys import (
    customer_sk_expr,
    product_sk_expr,
    store_sk_expr,
    location_sk_expr,
    normalize_unix_timestamp,
)


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("FactTest").getOrCreate()


def test_transform_to_fact_product_view(spark):
    events = [{
        "event_id": "e1",
        "user_id_db": "u1",
        "device_id": "d1",
        "product_id": "p1",
        "store_id": "s1",
        "ip": "1.1.1.1",
        "time_stamp": 1591266059,
    }]
    events_df = (
        spark.createDataFrame(events)
        .withColumn("time_stamp", normalize_unix_timestamp("time_stamp"))
    )

    # Dim stubs (not used for SK calculation anymore, but required by signature)
    dim_cust = spark.createDataFrame([{"user_id_db": "u1", "device_id": "d1", "customer_sk": "x"}])
    dim_prod = spark.createDataFrame([{"product_id": "p1", "product_sk": "x"}])
    dim_store = spark.createDataFrame([{"store_id": "s1", "store_sk": "x"}])
    dim_loc = spark.createDataFrame([{"ip": "1.1.1.1", "location_sk": "x"}])
    dim_date = spark.createDataFrame([{"date_sk": 20200604}])

    result_df = transform_to_fact_product_view(
        events_df, dim_cust, dim_prod, dim_store, dim_loc, dim_date
    )

    assert result_df.count() == 1
    row = result_df.collect()[0]

    expected = (
        events_df
        .withColumn("customer_sk", customer_sk_expr())
        .withColumn("product_sk", product_sk_expr(events_df.columns))
        .withColumn("store_sk", store_sk_expr())
        .withColumn("location_sk", location_sk_expr())
        .collect()[0]
    )

    assert row["customer_sk"] == expected["customer_sk"]
    assert row["product_sk"] == expected["product_sk"]
    assert row["store_sk"] == expected["store_sk"]
    assert row["location_sk"] == expected["location_sk"]
    assert row["date_sk"] == 20200604
    assert row["event_id"] == "e1"
