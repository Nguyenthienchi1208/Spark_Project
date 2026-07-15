import os
from config.logger_config import setup_logger

logger = setup_logger("ConfigSettings")

KAFKA_CONFIG = {
    "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    "topic": os.getenv("KAFKA_TOPIC", "product_view"),
    # latest = only new messages after the query starts (or checkpoint resume)
    "starting_offsets": os.getenv("KAFKA_STARTING_OFFSETS", "latest"),
    # Cap Kafka offsets per micro-batch to avoid driver/executor OOM
    "max_offsets_per_trigger": os.getenv("KAFKA_MAX_OFFSETS_PER_TRIGGER", "1000"),
    "fail_on_data_loss": os.getenv("KAFKA_FAIL_ON_DATA_LOSS", "false"),
    "security_protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_PLAINTEXT"),
    "sasl_mechanism": os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
    "sasl_jaas_config": os.getenv("KAFKA_SASL_JAAS_CONFIG"),
}

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

# Cấu hình JDBC cho Spark
DB_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

# Giữ nguyên cấu hình cũ nếu bạn vẫn cần dùng ở chỗ khác
POSTGRES_CONFIG = {
    "url": DB_URL,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver",
}

CHECKPOINT_PATH = "hdfs://namenode:9000/user/spark/checkpoints/streaming_job"