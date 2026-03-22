from pathvalidate import sanitize_filename
import os
from pyspark.sql import SparkSession

os.makedirs('data', exist_ok=True)
spark = SparkSession.builder \
    .appName('data preparation') \
    .master("local") \
    .config("spark.sql.parquet.enableVectorizedReader", "true") \
    .getOrCreate()


df = spark.read.parquet("/a.parquet")
n = 1000
df = df.select(['id', 'title', 'text']).filter(df.text.isNotNull()).limit(n)


def create_doc(row):
    filename = "data/" + sanitize_filename(str(row['id']) + "_" + row['title']).replace(" ", "_") + ".txt"
    with open(filename, "w") as f:
        f.write(row['text'])


df.foreach(create_doc)