# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09


# setup.py
from setuptools import setup, find_packages


def read_readme() -> str:
    """Why: Ensures PyPI uses your README.md as long_description."""
    try:
        with open('README.md', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ''


setup(
    name='txt_toolz',
    version='7.19.3',
    description='A pure-Python library for text processing, file handling, and lightweight NLP utilities.',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Isaac Onagh',
    author_email='mkalafsaz@gmail.com',
    packages=find_packages(),
    python_requires='>=3.8',
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
    ],
)
