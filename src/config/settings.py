import os
from config.logger_config import setup_logger

logger = setup_logger("ConfigSettings")

KAFKA_CONFIG = {
    "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "46.202.167.130:9094"),
    "topic": os.getenv("KAFKA_TOPIC", "product_view"),
    "starting_offsets": os.getenv("KAFKA_STARTING_OFFSETS", "latest"),
    "max_offsets_per_trigger": os.getenv("KAFKA_MAX_OFFSETS_PER_TRIGGER", "1000"),
    "fail_on_data_loss": os.getenv("KAFKA_FAIL_ON_DATA_LOSS", "false"),
    "security_protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_PLAINTEXT"),
    "sasl_mechanism": os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
    "sasl_jaas_config": os.getenv(
        "KAFKA_SASL_JAAS_CONFIG",
        "org.apache.kafka.common.security.plain.PlainLoginModule required username='username' password='password';"
    ),
}

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")


DB_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

POSTGRES_CONFIG = {
    "url": DB_URL,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver",
}

CHECKPOINT_PATH = "hdfs://namenode:9000/user/spark/checkpoints/streaming_job"