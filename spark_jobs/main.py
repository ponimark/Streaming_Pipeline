from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    window,
    col,
    collect_list,
    map_from_entries,
    struct,
    to_json,
    sum,
    max,
    when
)
from docs.logger_activate import logger

def main():
    # 1) Spark session
    try:
        logger.info("************ CREATING SPARK SESSION *******************")
        spark = SparkSession.builder.appName('apple') \
            .config('spark.jars', r"E:\Apple\docker\Drivers\postgresql-42.7.7.jar") \
            .getOrCreate()
        logger.info("************ SPARK SESSION CREATED *******************")

    except Exception as e:
        logger.error(f" Failed to create Spark session {e}")
        return

    # 2) Read from Postgres
    try:
        logger.info("************ CONNECTING TO DATABASE *******************")
        df = spark.read.format('jdbc') \
            .option('url', 'jdbc:postgresql://localhost:5432/postgres') \
            .option('dbtable', 'apple_app_aggregates') \
            .option('user', 'postgres') \
            .option('password', 'poni') \
            .option('driver', 'org.postgresql.Driver') \
            .load()
    except Exception as e:
        logger.error(f" Error reading from DATABASE {e}")
        return




    # 3) Per‑device aggregation per user‑hour
    try:
        logger.info("************ AGGREGATING PER DEVICE PER HOUR *******************")
        df = df.withColumn(
            "did_purchase_int",
            when(col("did_purchase")=="true", 1).otherwise(0)
        ).withColumn(
            "did_login_int",
            when(col("did_login")=="true", 1).otherwise(0)
        )

        per_device = (
            df.groupBy(
                col('user_id'),
                window(col('session_start'), '30 minute').alias('hour_window'),
                col('device')
            )
            .agg(
                sum("total_actions").alias("total_actions_sum_per_device"),
                sum("did_purchase_int").alias("purchase_per_device_sum"),
                sum("did_login_int").alias("logi_per_device_sum"),
            )
        )
    except Exception as e:
        logger.error(f" Error in per_device aggregation {e}")
        return



    # 4) Roll‑up to user‑hour, build device→count map & sum
    try:
        logger.info("************ BUILDING DEVICE COUNT MAP  *******************")
        agg = (
            per_device
            .groupBy('user_id', 'hour_window')
            .agg(
                sum("total_actions_sum_per_device").alias("actions"),
                max("purchase_per_device_sum").alias("any_purchase"),
                max("logi_per_device_sum").alias("any_login"),
                map_from_entries(
                    collect_list(
                        struct(col('device'), col('total_actions_sum_per_device'))
                    )
                ).alias("device_map")
            )
        )

    except Exception as e:
        logger.error(f" Error in creating map aggregation {e}")
        return

    # 5) Convert map to JSON
    try:
        logger.info("************ CONVERTING DEVICE MAP TO JSON *******************")
        result = agg.withColumn(
            "action_made_from_each_device",
            to_json(col("device_map"))
        )
        logger.info(" JSON conversion complete")
    except Exception as e:
        logger.error(f" Error converting device_map to JSON {e}")
        return

    # 6) Final select & display
    try:
        logger.info("************ SELECTING FINAL OUTPUT *******************")
        final = result.select(
            'user_id',
            col('hour_window.start').alias('window_start'),
            col('hour_window.end').alias('window_end'),
            'action_made_from_each_device',
            'actions',
            'any_purchase',
            'any_login',
        )
        final = final.withColumn(
            "any_purchase",
            when(col('any_purchase') == 1, "Yes").otherwise("No")
        ).withColumn(
            "any_login",
            when(col('any_login') == 1, "Yes").otherwise("No")
        )

        final.show(truncate=False)
        logger.info(" Final DataFrame ready")
    except Exception as e :
        logger.error(f" Error in final selection {e}")
        return


# WRITING INTO PARQUET AND STORING IN LOCAL
    logger.info(f"********** WRITING OUTPUT TO PARQUET AT E:\Apple\FINAL_DATA ***************** ")
    try:
        final.write.format('parquet')\
        .option('header','true')\
        .mode('overwrite')\
        .partitionBy('window_start')\
        .option('path','E:\Apple\FINAL_DATA')\
        .save()

    except Exception as e:
        logger.error(f" Error in writing final data {e}")

if __name__ == "__main__":
    main()


