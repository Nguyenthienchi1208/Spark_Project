from pyspark.sql import functions as F
from pyspark.sql.window import Window
from utils.surrogate_keys import customer_sk_expr


def transform_to_dim_customer(df):
    df_transformed = df.withColumn("customer_sk", customer_sk_expr())

    for col_name in ["user_id_db", "email_address", "device_id", "user_agent", "resolution"]:
        if col_name in df_transformed.columns:
            df_transformed = df_transformed.withColumn(col_name, F.col(col_name).cast("string"))

    order_col = "time_stamp" if "time_stamp" in df_transformed.columns else "customer_sk"
    window_spec = Window.partitionBy("customer_sk").orderBy(F.col(order_col).desc())

    return (
        df_transformed
        .withColumn("row_num", F.row_number().over(window_spec))
        .filter(F.col("row_num") == 1)
        .drop("row_num")
    )
