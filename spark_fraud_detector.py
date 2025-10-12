from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, DoubleType, StringType, LongType
import joblib
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import IntegerType

model = joblib.load("fraud_model.pkl")

spark = SparkSession.builder \
    .appName("FraudDetection") \
    .getOrCreate()

schema = StructType() \
    .add("user_id", LongType()) \
    .add("amount", DoubleType()) \
    .add("country", StringType()) \
    .add("timestamp", DoubleType())

raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transactions") \
    .load()

json_df = raw_df.selectExpr("CAST(value AS STRING)")
parsed_df = json_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

@pandas_udf(IntegerType())
def fraud_udf(amount, country):
    df = pd.DataFrame({"amount": amount, "country": country})
    df = pd.get_dummies(df)
    for col in model.feature_names_in_:
        if col not in df.columns:
            df[col] = 0
    return pd.Series(model.predict(df[model.feature_names_in_]))

final_df = parsed_df.withColumn("fraud", fraud_udf(col("amount"), col("country")))

query = final_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()