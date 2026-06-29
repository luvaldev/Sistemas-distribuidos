from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, window, expr, count, when
)
from pyspark.sql.types import (
    StructType, StringType, DoubleType,
    TimestampType, IntegerType
)

spark = SparkSession.builder \
    .appName("MetricasDistribuidos") \
    .config("spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
        "org.elasticsearch:elasticsearch-spark-30_2.12:8.8.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType() \
    .add("timestamp", TimestampType()) \
    .add("query_type", StringType()) \
    .add("latency", DoubleType()) \
    .add("cache_status", StringType()) \
    .add("retries", IntegerType()) \
    .add("status", StringType())

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "metrics-topic") \
    .option("startingOffsets", "latest") \
    .load()

parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("d")
).select("d.*")

agg = parsed.withWatermark("timestamp", "1 minute") \
    .groupBy(window(col("timestamp"), "1 minute")) \
    .agg(
        count(when(col("status") == "success", True)).alias("throughput"),
        expr("percentile_approx(latency, 0.5)").alias("p50_latency"),
        expr("percentile_approx(latency, 0.95)").alias("p95_latency"),
        (count(when(col("cache_status") == "hit", True))
         / count("*")).alias("hit_rate"),
        (count(when(col("retries") > 0, True))
         / count("*")).alias("retry_rate")
    )

final = agg.select(
    col("window.start").alias("@timestamp"),
    "throughput","p50_latency","p95_latency","hit_rate","retry_rate"
)

query = final.writeStream.format("es") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/spark-checkpoints") \
    .option("es.nodes", "localhost") \
    .option("es.port", "9200") \
    .option("es.resource", "metrics-index") \
    .start()

query.awaitTermination()
