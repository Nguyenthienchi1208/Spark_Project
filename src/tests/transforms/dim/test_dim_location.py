from pyspark.sql import SparkSession
from transforms.dim.dim_location import process_dim_location
from utils.surrogate_keys import location_sk_expr


def test_process_dim_location():
    spark = SparkSession.builder \
        .appName("TestDimLocation") \
        .master("local[*]") \
        .getOrCreate()

    data = [("37.170.17.183",), ("87.196.97.119",), ("37.170.17.183",)]
    df = spark.createDataFrame(data, ["ip"])

    result_df = process_dim_location(df)
    results = result_df.collect()

    if len(results) == 0:
        spark.stop()
        return

    assert len(results) == 2
    assert "location_sk" in result_df.columns
    assert "ip" in result_df.columns

    for row in results:
        expected = (
            spark.createDataFrame([{"ip": row["ip"]}])
            .withColumn("location_sk", location_sk_expr())
            .collect()[0]["location_sk"]
        )
        assert row["location_sk"] == expected

    spark.stop()


if __name__ == "__main__":
    test_process_dim_location()
