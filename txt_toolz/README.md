# PyTextUtils

**PyTextUtils** — a pure-Python library for text manipulation, file I/O, and lightweight NLP utilities.

## Features

- String / text utilities: snake_case ⇄ CamelCase conversion, whitespace normalization, punctuation stripping, palindrome check, dedent, reverse, word count, and more.
- File operations: read/write/append text or lines, streaming reading for large files.
- NLP tools (pure Python, no dependencies): tokenization, stopword removal, bag-of-words, TF, IDF, TF-IDF vectors, cosine similarity, similarity search among documents, keyword extraction.
- Flexible vectorization & document similarity workflows — build vocabularies, compute TF-IDF matrices, search similar documents without external libraries.

## Installation

```bash
pip install txt_toolz


## usage

import txt_toolz as tu

# Basic string utils
s = "Hello   World!"
print(tu.normalize_whitespace(s))        # "Hello World!"
print(tu.to_snake_case("HelloWorld"))    # "hello_world"

# File operations
tu.write_text("demo.txt", "Hello\nWorld")
print(tu.read_text("demo.txt"))

# NLP & similarity
docs = [
    "python code machine learning",
    "cooking recipes kitchen food",
    "deep learning neural network python",
]
vocab, idf_map, matrix = tu.tfidf_matrix(docs)
query = "python machine learning"
top = tu.search_similar(query, docs, top_n=2)
print(top)
```
