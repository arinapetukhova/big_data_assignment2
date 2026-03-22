from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName('create input data') \
    .master("local") \
    .getOrCreate()

rdd = spark.sparkContext.wholeTextFiles("hdfs://cluster-master:9000/data/*")

def parse_file(file_data):
    filepath, content = file_data
    filename = filepath.split('/')[-1]
    
    parts = filename.replace('.txt', '').split('_', 1)
    doc_id = parts[0]
    doc_title = parts[1]
    content_clean = content.replace('\t', ' ').replace('\n', ' ')
    
    return f"{doc_id}\t{doc_title}\t{content_clean}"

formatted_rdd = rdd.map(parse_file)
formatted_rdd.coalesce(1).saveAsTextFile("/input/data")
print("Created /input/data")