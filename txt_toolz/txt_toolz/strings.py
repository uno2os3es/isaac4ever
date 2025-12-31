# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

# txt_toolz/strings.py
from __future__ import annotations
import regex as re
import string
import textwrap


def to_snake_case(text: str) -> str:
    """Convert to snake_case."""
    text = re.sub(r'[\s\-]+', '_', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
    return text.lower()


def to_camel_case(text: str) -> str:
    """Convert to CamelCase."""
    parts = re.split(r'[\s\-_]+', text)
    return ''.join(p.capitalize() for p in parts if p)


def normalize_whitespace(text: str) -> str:
    """Collapse redundant whitespace."""
    return ' '.join(text.split())


def count_words(text: str) -> int:
    """Count words."""
    return len(re.findall(r'\b\w+\b', text))


def reverse(text: str) -> str:
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Check palindrome ignoring case + punctuation."""
    cleaned = strip_punctuation(text).replace(' ', '').lower()
    return cleaned == cleaned[::-1]


def strip_punctuation(text: str) -> str:
    table = str.maketrans('', '', string.punctuation)
    return text.translate(table)


def dedent(text: str) -> str:
    return textwrap.dedent(text)
