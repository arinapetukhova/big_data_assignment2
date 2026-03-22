#!/bin/bash

INPUT_PATH=${1:-/input/data}

echo "Building document statistics..."
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files mapreduce/mapper1.py \
    -mapper "python3 mapper1.py" \
    -reducer "cat" \
    -input $INPUT_PATH \
    -output /indexer/doc_stats

echo "Building corpus statistics..."
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files mapreduce/mapper2.py,mapreduce/reducer2.py \
    -mapper "python3 mapper2.py" \
    -reducer "python3 reducer2.py" \
    -input /indexer/doc_stats \
    -output /indexer/corpus_stats

echo "Building inverted index..."
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files mapreduce/mapper3.py,mapreduce/reducer3.py \
    -mapper "python3 mapper3.py" \
    -reducer "python3 reducer3.py" \
    -input $INPUT_PATH \
    -output /indexer/term_doc_counts

echo "Building vocabulary..."
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files mapreduce/mapper4.py,mapreduce/reducer4.py \
    -mapper "python3 mapper4.py" \
    -reducer "python3 reducer4.py" \
    -input /indexer/term_doc_counts \
    -output /indexer/vocabulary

echo "create_index.sh completed"
