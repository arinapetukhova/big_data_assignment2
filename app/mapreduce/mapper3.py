#!/usr/bin/env python3
import sys
import re

for document in sys.stdin:
    doc_id, doc_title, doc_text = document.split('\t')
    doc_text = doc_text.strip()
    if not doc_text:
        continue
    
    doc_text = doc_text.lower()
    doc_text = re.sub(r'[^\w\s]', '', doc_text)
    words = doc_text.split()

    term_counts = {}
    for word in words:
        if word:
            term_counts[word] = term_counts.get(word, 0) + 1
    
    for term, tf in term_counts.items():
        print(f"{term}\t{doc_id}\t{tf}")
