# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09


# tests/test_files.py
import os
import txt_toolz as t


def test_file_ops(tmp_path):
    p = tmp_path / 'f.txt'

    t.write_text(p, 'abc')
    assert t.read_text(p) == 'abc'

    t.append_text(p, '123')
    assert t.read_text(p) == 'abc123'

    t.write_lines(p, ['a\n', 'b\n'])
    assert t.read_lines(p) == ['a\n', 'b\n']


def test_stream_read(tmp_path):
    p = tmp_path / 'big.txt'
    t.write_text(p, 'abcdef' * 100)
    chunks = list(t.stream_read(p, chunk_size=50))
    assert len(chunks) > 1
    assert ''.join(chunks).startswith('abcdef')
