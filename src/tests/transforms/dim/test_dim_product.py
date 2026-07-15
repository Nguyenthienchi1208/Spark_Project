import pytest
from pyspark.sql import SparkSession
from transforms.dim.dim_product import transform_to_dim_product
from utils.surrogate_keys import product_sk_expr


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("ETL_Test").getOrCreate()


def test_transform_to_dim_product_full_data(spark):
    data = [
        {
            "product_id": "89592",
            "collection": "checkout",
            "option": [{"option_label": "alloy", "value_label": "white-585"}],
        }
    ]
    df = spark.createDataFrame(data)
    result_df = transform_to_dim_product(df)

    assert result_df.count() == 1
    row = result_df.collect()[0]
    assert row["alloy"] == "white-585"
    assert row["product_id"] == "89592"
    expected_sk = df.withColumn("product_sk", product_sk_expr(df.columns)).collect()[0]["product_sk"]
    assert row["product_sk"] == expected_sk


def test_transform_to_dim_product_missing_columns(spark):
    data = [{"product_id": "12345"}]
    df = spark.createDataFrame(data)

    result_df = transform_to_dim_product(df)

    assert result_df.count() == 1
    assert "product_sk" in result_df.columns
    row = result_df.collect()[0]
    assert row["product_id"] == "12345"
    assert row["alloy"] is None
    expected_sk = df.withColumn("product_sk", product_sk_expr(df.columns)).collect()[0]["product_sk"]
    assert row["product_sk"] == expected_sk
