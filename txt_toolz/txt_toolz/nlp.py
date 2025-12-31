# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

# txt_toolz/nlp.py
from __future__ import annotations
from typing import Dict, List, Set
import math
from .advanced import tokenize


def load_stopwords() -> Set[str]:
    """Lightweight English stopword list."""
    return {
        'the',
        'a',
        'an',
        'and',
        'or',
        'but',
        'if',
        'while',
        'in',
        'on',
        'at',
        'by',
        'to',
        'from',
        'of',
        'for',
        'is',
        'are',
        'was',
        'were',
        'be',
        'been',
        'being',
        'this',
        'that',
        'these',
        'those',
        'it',
        'its',
    }


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Drop common English stopwords."""
    sw = load_stopwords()
    return [t for t in tokens if t not in sw]


def token_freq(tokens: List[str]) -> Dict[str, int]:
    """Token → frequency map."""
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    return freq


def build_vocab(docs: List[str]) -> List[str]:
    """Build global vocabulary across docs."""
    vocab = set()
    for d in docs:
        vocab.update(tokenize(d))
    return sorted(vocab)


def bow_vector(tokens: List[str], vocab: List[str]) -> List[int]:
    """Bag-of-words vector using given vocab ordering."""
    freq = token_freq(tokens)
    return [freq.get(word, 0) for word in vocab]


def tf(tokens: List[str]) -> Dict[str, float]:
    """Term frequency map."""
    freq = token_freq(tokens)
    total = len(tokens)
    return {t: f / total for t, f in freq.items()}


def idf(docs: List[str]) -> Dict[str, float]:
    """Compute IDF across documents."""
    total_docs = len(docs)
    doc_freq = {}

    for d in docs:
        seen = set(tokenize(d))
        for tok in seen:
            doc_freq[tok] = doc_freq.get(tok, 0) + 1

    return {
        t: math.log((1 + total_docs) / (1 + df)) + 1
        for t, df in doc_freq.items()
    }


def tfidf(tokens: List[str], idf_map: Dict[str, float]) -> Dict[str, float]:
    """Compute TF-IDF vector for a token list."""
    tf_map = tf(tokens)
    return {t: tf_map.get(t, 0) * idf_map.get(t, 0) for t in idf_map}


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def extract_keywords(text: str, docs: List[str], top_k: int = 5) -> List[str]:
    """Return top-k TF-IDF keywords."""
    tokens = remove_stopwords(tokenize(text))
    idf_map = idf(docs)
    scores = tfidf(tokens, idf_map)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in ranked[:top_k]]


# --- TF-IDF full matrix + similarity search --------------------


def tfidf_vector(
    tokens: List[str], vocab: List[str], idf_map: Dict[str, float]
) -> List[float]:
    """Convert tokens into a TF-IDF vector matching vocab order."""
    tf_map = tf(tokens)
    return [tf_map.get(w, 0.0) * idf_map.get(w, 0.0) for w in vocab]


def tfidf_matrix(docs: List[str]) -> tuple:
    """
    Build:
      - vocab list
      - idf map
      - document TF-IDF matrix (list of vectors)
    """
    vocab = build_vocab(docs)
    idf_map = idf(docs)
    matrix = [tfidf_vector(tokenize(doc), vocab, idf_map) for doc in docs]
    return vocab, idf_map, matrix


def cosine_similarity_matrix(matrix: List[List[float]]) -> List[List[float]]:
    """
    Compute NxN cosine similarity matrix for TF-IDF vector list.
    """
    n = len(matrix)
    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sim[i][j] = cosine_similarity(matrix[i], matrix[j])
    return sim


def search_similar(query: str, docs: List[str], top_n: int = 5) -> List[tuple]:
    """
    Rank documents by similarity to a query using TF-IDF + cosine.
    Returns: list of (doc_index, score)
    """
    vocab, idf_map, matrix = tfidf_matrix(docs)
    q_vec = tfidf_vector(tokenize(query), vocab, idf_map)

    scores = [
        (i, cosine_similarity(q_vec, vec)) for i, vec in enumerate(matrix)
    ]
    ranked = sorted(scores, key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def vectorize_docs(docs: List[str]) -> dict:
    """
    Utility helper: return vocab, idf_map, and matrix
    for reuse across multiple similarity searches.
    """
    vocab, idf_map, matrix = tfidf_matrix(docs)
    return {
        'vocab': vocab,
        'idf': idf_map,
        'matrix': matrix,
    }
