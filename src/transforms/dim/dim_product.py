from pyspark.sql import functions as F
from pyspark.sql.window import Window
from utils.surrogate_keys import product_sk_expr, UNKNOWN_SK


def transform_to_dim_product(df):
    potential_pid_cols = ["product_id", "recommendation_product_id", "viewing_product_id"]
    available_pid_cols = [c for c in potential_pid_cols if c in df.columns]

    if not available_pid_cols:
        return df.filter(F.lit(False))

    df_base = (
        df.withColumn("product_sk", product_sk_expr(df.columns))
        .withColumn(
            "product_id",
            F.coalesce(*[F.when(F.trim(F.col(c)) == "", F.lit(None)).otherwise(F.col(c)) for c in available_pid_cols]),
        )
        .filter((F.col("product_sk").isNotNull()) & (F.col("product_sk") != UNKNOWN_SK))
    )

    if "collection" not in df_base.columns:
        df_base = df_base.withColumn("collection", F.lit(None).cast("string"))

    if "option" in df_base.columns:
        df_transformed = (
            df_base
            .withColumn(
                "alloy",
                F.expr("get(filter(option, x -> x.option_label == 'alloy'), 0).value_label"),
            )
            .withColumn(
                "diamond",
                F.expr("get(filter(option, x -> x.option_label == 'diamond'), 0).value_label"),
            )
        )
    else:
        df_transformed = df_base.withColumn("alloy", F.lit(None)).withColumn("diamond", F.lit(None))

    window_spec = Window.partitionBy("product_sk").orderBy(F.col("collection").desc_nulls_last())

    return (
        df_transformed
        .withColumn("row_num", F.row_number().over(window_spec))
        .filter(F.col("row_num") == 1)
        .select("product_sk", "product_id", "collection", "alloy", "diamond")
    )
