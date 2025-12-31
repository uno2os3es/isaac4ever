# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09


# tests/test_strings.py
import txt_toolz as t


def test_snake_case():
    assert t.to_snake_case('HelloWorld') == 'hello_world'
    assert t.to_snake_case('Hello World') == 'hello_world'


def test_camel_case():
    assert t.to_camel_case('hello world') == 'HelloWorld'


def test_whitespace():
    assert t.normalize_whitespace('a   b\n c') == 'a b c'


def test_palindrome():
    assert t.is_palindrome("Madam, I'm Adam")
    assert not t.is_palindrome('Hello')


def test_count_words():
    assert t.count_words('one two three') == 3
