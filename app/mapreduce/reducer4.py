#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    
    if not line:
        continue
    
    try:
        term, docs = line.split('\t')
        print(f"{term}\t{len(docs.split(','))}")
    except ValueError:
        continue
