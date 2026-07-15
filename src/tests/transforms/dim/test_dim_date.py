from pyspark.sql import SparkSession
from transforms.dim.dim_date import transform_to_dim_date
from utils.surrogate_keys import normalize_unix_timestamp


def test_transform_to_dim_date_from_unix_seconds():
    spark = SparkSession.builder.appName("TestDimDate").master("local[*]").getOrCreate()

    # 1591266059 = 2020-06-04 (UTC epoch seconds)
    data = [{"time_stamp": 1591266059}, {"time_stamp": 1591266059}]
    df = spark.createDataFrame(data).withColumn(
        "time_stamp", normalize_unix_timestamp("time_stamp")
    )

    result_df = transform_to_dim_date(df)
    assert result_df.count() == 1
    row = result_df.collect()[0]
    assert row["year"] == 2020
    assert row["month"] == 6
    assert row["date_sk"] == 20200604
    assert row["full_date"] is not None

    spark.stop()


if __name__ == "__main__":
    test_transform_to_dim_date_from_unix_seconds()
