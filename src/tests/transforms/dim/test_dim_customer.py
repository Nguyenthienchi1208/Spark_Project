import pytest
from pyspark.sql import SparkSession
from transforms.dim.dim_customer import transform_to_dim_customer
from utils.surrogate_keys import customer_sk_expr


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("CustomerTest").getOrCreate()


def test_transform_to_dim_customer(spark):
    data = [{
        "user_id_db": "502567",
        "email_address": "pereira.vivien@yahoo.fr",
        "device_id": "beb2cacb-20af-4f05-9c03-c98e54a1b71a",
        "user_agent": "Mozilla/5.0",
        "resolution": "375x667",
        "time_stamp": 1591266092,
    }]
    df = spark.createDataFrame(data)

    result_df = transform_to_dim_customer(df)

    assert result_df.count() == 1
    row = result_df.collect()[0]
    assert row["email_address"] == "pereira.vivien@yahoo.fr"
    assert row["user_id_db"] == "502567"
    expected_sk = df.withColumn("customer_sk", customer_sk_expr()).collect()[0]["customer_sk"]
    assert row["customer_sk"] == expected_sk


def test_customer_sk_falls_back_to_device_id(spark):
    data = [{
        "user_id_db": "",
        "device_id": "device-abc",
        "email_address": None,
        "user_agent": "ua",
        "resolution": "1x1",
        "time_stamp": 1591266092,
    }]
    df = spark.createDataFrame(data)
    row = transform_to_dim_customer(df).collect()[0]
    expected_sk = df.withColumn("customer_sk", customer_sk_expr()).collect()[0]["customer_sk"]
    assert row["customer_sk"] == expected_sk
    assert row["customer_sk"] != "-1"
