# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup, find_packages

# Try to use Cython if available, otherwise use pre-compiled C

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='fileutils',
    version='1.1.7',
    author='Isaac Onagh',
    author_email='mkalafsaz@gmail.com',
    description='A comprehensive Python package for handling files and folders',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.7',
    install_requires=[],
)
