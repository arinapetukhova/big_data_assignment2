#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, explode, log, col, lit
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, IntegerType
import sys
import re

query = sys.argv[1]
print(f"Query: {query}")

spark = SparkSession.builder \
    .appName("BM25 Search Engine") \
    .config("spark.cassandra.connection.host", "scylladb-server") \
    .getOrCreate()

vocab_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="vocabulary", keyspace="search_engine") \
    .load()

inverted_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="inverted_index", keyspace="search_engine") \
    .load()

doc_stats_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="document_stats", keyspace="search_engine") \
    .load()

corpus_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="corpus_stats", keyspace="search_engine") \
    .load()

corpus_row = corpus_df.collect()[0]
N = corpus_row.total_docs
avg_dl = corpus_row.avg_doc_length
k1 = 1.0
b = 0.75

print(f"Corpus: {N} documents, avg length: {avg_dl:.2f}")

query_lower = query.lower()
query_terms = set(re.findall(r'\w+', query_lower))
print(f"Query terms: {query_terms}")

relevant_vocab = vocab_df.filter(vocab_df.term.isin(query_terms))
relevant_count = relevant_vocab.count()
print(f"Found {relevant_count} matching terms")

if relevant_count == 0:
    print("No matching terms found")
    spark.stop()
    sys.exit(0)

query_inverted = inverted_df.join(relevant_vocab, "term")
posting_schema = ArrayType(
    StructType([
        StructField("doc_id", StringType()),
        StructField("tf", IntegerType())
    ])
)

def parse_postings(postings_str):
    result = []
    for posting in postings_str.split(','):
        if ':' in posting:
            doc_id, tf = posting.split(':')
            result.append((doc_id, int(tf)))
    return result

parse_udf = udf(parse_postings, posting_schema)

exploded_df = query_inverted \
    .select("term", "df", explode(parse_udf("postings")).alias("posting")) \
    .select("term", "df", "posting.doc_id", "posting.tf")
with_doc_stats = exploded_df.join(doc_stats_df, "doc_id")

idf = log(lit(N) / col("df"))
tf_component = ((k1 + 1) * col("tf")) / (k1 * (1 - b + b * (col("doc_length") / lit(avg_dl))) + col("tf"))
score = idf * tf_component

with_scores = with_doc_stats.withColumn("score", score)
doc_scores = with_scores.groupBy("doc_id", "title").sum("score")
top_10 = doc_scores.orderBy(col("sum(score)").desc()).limit(10).collect()

print("\n\n")
print(f"Search Results for: \"{query}\"")

if not top_10:
    print("No matching documents found.")
else:
    for i, row in enumerate(top_10, 1):
        print(f"{i:2}. doc_id: {row.doc_id} - {row.title} (score: {row['sum(score)']:.4f})")

print("\n\n")
spark.stop()
