#!/usr/bin/env python3
import sys

current_word = None
doc_tf = {} 
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    try:
        word, doc_id, tf = line.split('\t')
        tf = int(tf)
    except ValueError:
        continue
    
    if current_word and word != current_word:
        posting_parts = [f"{doc}:{doc_tf[doc]}" for doc in sorted(doc_tf.keys())]
        print(f"{current_word}\t{','.join(posting_parts)}")
        current_word = word
        doc_tf = {doc_id: tf}
    
    elif not current_word:
        current_word = word
        doc_tf = {doc_id: tf}

    else:
        doc_tf[doc_id] = tf

if current_word:
    posting_parts = [f"{doc}:{doc_tf[doc]}" for doc in sorted(doc_tf.keys())]
    print(f"{current_word}\t{','.join(posting_parts)}")