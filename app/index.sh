#!/bin/bash

echo "Creating index in HDFS..."
bash create_index.sh

echo "Storing index to ScyllaDB..."
bash store_index.sh

echo "Indexing complete"
