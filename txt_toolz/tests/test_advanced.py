# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09


# tests/test_advanced.py
import txt_toolz as t


def test_tokenize():
    assert t.tokenize('Hello, world!') == ['hello', 'world']


def test_sentence_split():
    assert t.tokenize_sentences('A. B? C!') == ['A', 'B', 'C']


def test_ngrams():
    tokens = ['a', 'b', 'c']
    assert t.ngrams(tokens, 2) == [('a', 'b'), ('b', 'c')]


def test_contains_find():
    text = 'Hello hello HeLLo'
    assert t.contains(text, 'hello')
    assert t.find_all(text, 'hello') == [0, 6, 12]


def test_stem():
    assert t.simple_stem('running') == 'runn'
    assert t.simple_stem('tests') == 'test'
    assert t.simple_stem('fly') == 'fly'
