
from pyspark.sql.types import StructType, StructField, StringType, LongType, ArrayType


option_schema = StructType([
    StructField("alloy", StringType(), True),
    StructField("diamond", StringType(), True),
    StructField("shapediamond", StringType(), True),
    StructField("stone", StringType(), True),
    StructField("quality", StringType(), True),
    StructField("quality_label", StringType(), True),
    StructField("finish", StringType(), True),
    StructField("pearlcolor", StringType(), True),
    StructField("option_id", StringType(), True),
    StructField("option_label", StringType(), True),
    StructField("value_id", StringType(), True),
    StructField("value_label", StringType(), True),
    StructField("price", StringType(), True),
    StructField("category_id", StringType(), True),
    StructField("Kollektion", StringType(), True),
    StructField("kollektion_id", StringType(), True)
])


cart_products_schema = StructType([
    StructField("product_id", StringType(), True),
    StructField("amount", StringType(), True),
    StructField("price", StringType(), True),
    StructField("currency", StringType(), True),
    # Trong cart_products lại có một mảng option nhỏ hơn nữa
    StructField("option", ArrayType(option_schema), True)
])


GLAMIRA_EVENT_SCHEMA = StructType([
    StructField("_id", StringType(), True),
    StructField("ip", StringType(), True),
    StructField("user_agent", StringType(), True),
    StructField("resolution", StringType(), True),
    StructField("user_id_db", StringType(), True),
    StructField("device_id", StringType(), True),
    StructField("api_version", StringType(), True),
    StructField("store_id", StringType(), True),
    StructField("time_stamp", LongType(), True),
    StructField("local_time", StringType(), True),
    StructField("show_recommendation", StringType(), True),
    StructField("current_url", StringType(), True),
    StructField("referrer_url", StringType(), True),
    StructField("email_address", StringType(), True),
    StructField("collection", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("cat_id", StringType(), True),
    StructField("collect_id", StringType(), True),
    StructField("currency", StringType(), True),
    StructField("price", StringType(), True),
    StructField("key_search", StringType(), True),
    StructField("utm_source", StringType(), True),
    StructField("utm_medium", StringType(), True),
    StructField("recommendation", StringType(), True),
    StructField("recommendation_product_id", StringType(), True),
    StructField("recommendation_product_position", StringType(), True),
    StructField("recommendation_clicked_position", StringType(), True),
    StructField("viewing_product_id", StringType(), True),
    StructField("is_paypal", StringType(), True),
    StructField("order_id", StringType(), True),
    StructField("option", ArrayType(option_schema), True),
    StructField("cart_products", ArrayType(cart_products_schema), True),
])