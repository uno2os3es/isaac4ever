# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09


import txt_toolz as t


def test_stopwords():
    tokens = ['this', 'is', 'car']
    assert t.remove_stopwords(tokens) == ['car']


def test_tf():
    assert t.tf(['a', 'a', 'b']) == {'a': 2 / 3, 'b': 1 / 3}


def test_idf():
    docs = ['a b', 'a c']
    idf_map = t.idf(docs)
    assert 'a' in idf_map
    assert 'b' in idf_map
    assert 'c' in idf_map


def test_tfidf():
    docs = ['apple banana', 'apple orange']
    idf_map = t.idf(docs)
    tokens = ['banana']
    vec = t.tfidf(tokens, idf_map)
    assert vec['banana'] > 0


def test_cosine_similarity():
    assert t.cosine_similarity([1, 0], [1, 0]) == 1.0
    assert t.cosine_similarity([1, 0], [0, 1]) == 0.0


def test_extract_keywords():
    docs = [
        'python code machine learning',
        'python code deep learning',
        'python code data processing',
    ]
    res = t.extract_keywords('machine learning python code', docs, top_k=2)
    assert len(res) == 2
