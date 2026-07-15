import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from transforms.dim.dim_store import transform_to_dim_store
from utils.surrogate_keys import store_sk_expr


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("StoreDimTest").getOrCreate()


def test_transform_to_dim_store(spark):
    schema = StructType([StructField("store_id", StringType(), True)])
    df = spark.createDataFrame([("101",), ("101",), ("102",), (None,)], schema)
    result_df = transform_to_dim_store(df)

    assert result_df.count() == 2
    assert "store_sk" in result_df.columns
    assert result_df.schema["store_sk"].dataType == StringType()

    rows = {r["store_id"]: r["store_sk"] for r in result_df.collect()}
    expected_101 = (
        spark.createDataFrame([("101",)], schema)
        .withColumn("store_sk", store_sk_expr())
        .collect()[0]["store_sk"]
    )
    assert rows["101"] == expected_101
