from pyspark.sql.functions import col, from_json
from schemas.data_schema import GLAMIRA_EVENT_SCHEMA

def get_kafka_stream(spark, kafka_config):
    reader = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_config["bootstrap_servers"])
        .option("subscribe", kafka_config["topic"])
        .option("startingOffsets", kafka_config["starting_offsets"])
        .option("maxOffsetsPerTrigger", kafka_config["max_offsets_per_trigger"])
        .option("failOnDataLoss", kafka_config.get("fail_on_data_loss", "false"))
        .option("kafka.security.protocol", kafka_config["security_protocol"])
        .option("kafka.sasl.mechanism", kafka_config["sasl_mechanism"])
        .option("kafka.sasl.jaas.config", kafka_config["sasl_jaas_config"])
    )

    return reader.load()

def transform_stream(raw_df):
    """Parse Kafka JSON and rename `_id` → `event_id` for the warehouse contract."""
    return (
        raw_df
        .selectExpr("CAST(value AS STRING) as json_payload")
        .select(from_json(col("json_payload"), GLAMIRA_EVENT_SCHEMA).alias("data"))
        .select("data.*")
        .withColumnRenamed("_id", "event_id")
    )