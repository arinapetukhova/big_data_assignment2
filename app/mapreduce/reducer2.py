#!/usr/bin/env python3
import sys

total_doc = 0
doc_lengths = 0

for line in sys.stdin:
    line = line.strip()
    
    if not line:
        continue
    
    try:
        doc_id, doc_title, doc_length = line.split('\t')
        total_doc += 1
        doc_lengths += int(doc_length)
    except ValueError:
        continue


print(f"{total_doc}\t{doc_lengths / total_doc}")
