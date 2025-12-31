# textutils/advanced.py
from __future__ import annotations
import regex as re
from typing import Iterable, Iterator, List, Tuple


def tokenize(text: str) -> List[str]:
    """Split text into lowercase alphanumeric tokens."""
    return re.findall(r'\b\w+\b', text.lower())


def tokenize_sentences(text: str) -> List[str]:
    """Split into sentences using punctuation boundaries."""
    parts = re.split(r'[.!?]+', text)
    return [s.strip() for s in parts if s.strip()]


def ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    """Return list of n-grams."""
    if n <= 0:
        raise ValueError('n must be >= 1')
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def contains(text: str, query: str) -> bool:
    """Case-insensitive substring lookup."""
    return query.lower() in text.lower()


def find_all(text: str, query: str) -> List[int]:
    """Return all start indices of (case-insensitive) query matches."""
    pattern = re.escape(query)
    return [m.start() for m in re.finditer(pattern, text, flags=re.I)]


def simple_stem(word: str) -> str:
    """Very naive suffix-based English stemmer."""
    suffixes = ['ing', 'ed', 'ly', 'es', 's']
    for s in suffixes:
        if word.endswith(s) and len(word) > len(s) + 2:
            return word[: -len(s)]
    return word


def stream_read(path: str, chunk_size: int = 4096) -> Iterator[str]:
    """Yield file chunks for streaming large files (reads in pieces)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk  # why: stream file incrementally without loading whole file
    except FileNotFoundError:
        raise
