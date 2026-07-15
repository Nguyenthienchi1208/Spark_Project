# File: utils/postgres_handler.py
from config.settings import POSTGRES_CONFIG, logger

def get_jdbc_url():
    return POSTGRES_CONFIG["url"]

def get_db_properties():
    return {
        "user": POSTGRES_CONFIG["user"],
        "password": POSTGRES_CONFIG["password"],
        "driver": POSTGRES_CONFIG["driver"]
    }

def write_to_postgres(df, table_name, mode="append"):
    """Ghi DataFrame vào Postgres."""
    if df is None or df.rdd.isEmpty():
        return
    
    try:
        df.write.format("jdbc") \
            .option("url", get_jdbc_url()) \
            .option("dbtable", table_name) \
            .option("user", get_db_properties()["user"]) \
            .option("password", get_db_properties()["password"]) \
            .option("driver", get_db_properties()["driver"]) \
            .mode(mode) \
            .save()
        logger.info(f"✅ Đã ghi thành công vào bảng {table_name}")
    except Exception as e:
        logger.error(f"❌ Lỗi ghi vào bảng {table_name}: {str(e)}")
        raise e

def read_from_postgres(spark, query):
    """Đọc dữ liệu từ Postgres."""
    try:
        return spark.read.format("jdbc") \
            .option("url", get_jdbc_url()) \
            .option("dbtable", f"({query}) AS temp_query") \
            .option("user", get_db_properties()["user"]) \
            .option("password", get_db_properties()["password"]) \
            .option("driver", get_db_properties()["driver"]) \
            .load()
    except Exception as e:
        logger.error(f"❌ Lỗi đọc từ Postgres: {str(e)}")
        raise e

def execute_upsert_query(query):
    """Thực thi SQL trực tiếp qua JDBC (Không dùng jpype)."""
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    
    conn = None
    try:
        driver_manager = spark._jvm.java.sql.DriverManager
        conn = driver_manager.getConnection(
            get_jdbc_url(), 
            get_db_properties()["user"], 
            get_db_properties()["password"]
        )
        
        with conn.createStatement() as stmt:
            stmt.execute(query)
            
        logger.info("✅ Lệnh SQL đã thực thi thành công.")
    except Exception as e:
        logger.error(f"❌ Lỗi thực thi SQL: {str(e)}")
        raise e
    finally:
        if conn is not None:
            conn.close()