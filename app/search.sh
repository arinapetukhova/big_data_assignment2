#!/bin/bash
echo "This script will include commands to search for documents given the query using Spark RDD"

if [ $# -eq 0 ]; then
    echo "ERROR: No query provided"
    exit 1
fi

QUERY="$1"
source .venv/bin/activate

export PYSPARK_DRIVER_PYTHON=$(which python)
export PYSPARK_PYTHON=./.venv/bin/python

spark-submit \
    --master yarn \
    --packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.0 \
    --conf spark.cassandra.connection.host=scylladb-server \
    --archives /app/.venv.tar.gz#.venv \
    query.py "$QUERY"

# spark-submit \
#     --master local[2] \
#     --packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.0 \
#     --conf spark.cassandra.connection.host=scylladb-server \
#     query.py "$QUERY"