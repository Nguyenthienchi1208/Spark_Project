from config.settings import POSTGRES_CONFIG, logger
import os

# Hàm bổ trợ để lấy config an toàn
def _get_config():
    # Kiểm tra nếu POSTGRES_CONFIG bị empty do lỗi scope khi chạy trên Worker
    if not POSTGRES_CONFIG or "url" not in POSTGRES_CONFIG:
        return {
            "url": os.getenv("DB_URL"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "driver": "org.postgresql.Driver"
        }
    return POSTGRES_CONFIG

def write_to_postgres(df, table_name, mode="append"):
    if df is None or df.rdd.isEmpty():
        return
    
    config = _get_config()
    
    # BẮT LỖI NGAY TẠI ĐÂY
    if not config.get("url") or not config.get("user") or not config.get("password"):
        error_msg = f"Cấu hình Postgres bị thiếu: {config}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        df.write.format("jdbc") \
            .option("url", config["url"]) \
            .option("dbtable", table_name) \
            .option("user", config["user"]) \
            .option("password", config["password"]) \
            .option("driver", config.get("driver", "org.postgresql.Driver")) \
            .mode(mode) \
            .save()
        logger.info(f"✅ Đã ghi thành công vào bảng {table_name}")
    except Exception as e:
        logger.error(f"❌ Lỗi ghi vào bảng {table_name}: {str(e)}")
        raise e

def read_from_postgres(spark, query):
    """Hàm đọc dữ liệu từ Postgres bổ sung lại cho bạn"""
    config = _get_config()
    try:
        return spark.read.format("jdbc") \
            .option("url", config["url"]) \
            .option("dbtable", f"({query}) AS temp_query") \
            .option("user", config["user"]) \
            .option("password", config["password"]) \
            .option("driver", config.get("driver", "org.postgresql.Driver")) \
            .load()
    except Exception as e:
        logger.error(f"❌ Lỗi đọc từ Postgres: {str(e)}")
        raise e