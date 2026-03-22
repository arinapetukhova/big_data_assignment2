#!/usr/bin/env python3
from cassandra.cluster import Cluster
import subprocess

cluster = Cluster(['scylladb-server'])
session = cluster.connect()

print("Creating schema...")
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS search_engine 
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")
session.set_keyspace('search_engine')

session.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary (
        term text PRIMARY KEY,
        df int
    )
""")
session.execute("""
    CREATE TABLE IF NOT EXISTS inverted_index (
        term text PRIMARY KEY,
        postings text
    )
""")
session.execute("""
    CREATE TABLE IF NOT EXISTS document_stats (
        doc_id text PRIMARY KEY,
        title text,
        doc_length int
    )
""")
session.execute("""
    CREATE TABLE IF NOT EXISTS corpus_stats (
        id int PRIMARY KEY,
        total_docs int,
        avg_doc_length float
    )
""")
print("Schema created")

print("Loading vocabulary...")
result = subprocess.run(
    ['hdfs', 'dfs', '-cat', '/indexer/vocabulary/part-*'],
    capture_output=True, text=True
)

for line in result.stdout.strip().split('\n'):
    if line and '\t' in line:
        term, df = line.split('\t')
        session.execute(
            "INSERT INTO vocabulary (term, df) VALUES (%s, %s)",
            (term, int(df))
        )
print(f"Loaded vocabulary")

print("Loading inverted index...")
result = subprocess.run(
    ['hdfs', 'dfs', '-cat', '/indexer/term_doc_counts/part-*'],
    capture_output=True, text=True
)

for line in result.stdout.strip().split('\n'):
    if line and '\t' in line:
        term, postings = line.split('\t')
        session.execute(
            "INSERT INTO inverted_index (term, postings) VALUES (%s, %s)",
            (term, postings)
        )
print(f"Loaded inverted index")

print("Loading document stats...")
result = subprocess.run(
    ['hdfs', 'dfs', '-cat', '/indexer/doc_stats/part-*'],
    capture_output=True, text=True
)

for line in result.stdout.strip().split('\n'):
    if line and '\t' in line:
        parts = line.split('\t')
        if len(parts) == 3:
            doc_id, title, length = parts
            session.execute(
                "INSERT INTO document_stats (doc_id, title, doc_length) VALUES (%s, %s, %s)",
                (doc_id, title, int(length))
            )
print(f"Loaded document stats")

print("Loading corpus stats...")
result = subprocess.run(
    ['hdfs', 'dfs', '-cat', '/indexer/corpus_stats/part-*'],
    capture_output=True, text=True
)

for line in result.stdout.strip().split('\n'):
    if line and '\t' in line:
        total_docs, avg_length = line.split('\t')
        session.execute(
            "INSERT INTO corpus_stats (id, total_docs, avg_doc_length) VALUES (1, %s, %s)",
            (int(total_docs), float(avg_length))
        )
print(f"Loaded corpus stats")

cluster.shutdown()
print("All data loaded successfully")
