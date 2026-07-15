from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import os

from utils.surrogate_keys import location_sk_expr, UNKNOWN_SK

_MMDB_CANDIDATES = (
    "/opt/spark/app/src/data/GeoLite2-City.mmdb",
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "GeoLite2-City.mmdb"),
)


def _resolve_mmdb_path():
    return next((os.path.normpath(p) for p in _MMDB_CANDIDATES if os.path.exists(os.path.normpath(p))), None)


def process_dim_location(df):
    mmdb_path = _resolve_mmdb_path()

    def process_partition(iterator):
        # Open the GeoIP DB once per partition (not per IP)
        reader = None
        try:
            if not mmdb_path:
                return
            try:
                import maxminddb
            except ImportError:
                # Workers without maxminddb → skip geo enrichment, don't crash the batch
                return
            reader = maxminddb.open_database(mmdb_path)

            for row in iterator:
                ip = row["ip"].strip() if row["ip"] else None
                if not ip:
                    continue
                try:
                    data = reader.get(ip)
                except Exception:
                    continue
                if not data:
                    continue
                country = data.get("country", {}).get("names", {}).get("en")
                subdivisions = data.get("subdivisions", [{}])
                region = subdivisions[0].get("names", {}).get("en") if subdivisions else None
                city = data.get("city", {}).get("names", {}).get("en")
                lat = data.get("location", {}).get("latitude")
                lon = data.get("location", {}).get("longitude")
                if country or lat:
                    yield (
                        ip,
                        country,
                        region,
                        city,
                        float(lat) if lat else 0.0,
                        float(lon) if lon else 0.0,
                    )
        finally:
            if reader is not None:
                reader.close()

    spark = df.sparkSession
    rdd = df.select("ip").distinct().rdd.mapPartitions(process_partition)

    schema = StructType([
        StructField("ip", StringType(), True),
        StructField("country", StringType(), True),
        StructField("region", StringType(), True),
        StructField("city", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
    ])

    df_dim = spark.createDataFrame(rdd, schema)
    if df_dim.limit(1).count() == 0:
        return spark.createDataFrame([], StructType(schema.fields + [
            StructField("location_sk", StringType(), True),
        ])).select(
            "location_sk", "ip", "country", "region", "city", "latitude", "longitude"
        )

    df_dim = df_dim.withColumn("location_sk", location_sk_expr())
    df_dim = df_dim.filter(F.col("location_sk") != UNKNOWN_SK)

    return df_dim.dropDuplicates(["location_sk"]).select(
        "location_sk", "ip", "country", "region", "city", "latitude", "longitude"
    )
