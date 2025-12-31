# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import sys
import os

# Check if Cython is available
try:
    from Cython.Build import cythonize

    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# Define extensions
extensions = [
    Extension(
        'fileutils.hashutil',
        ['fileutils/hashutil.pyx'],
        libraries=[],
        extra_compile_args=['-O3'] if sys.platform != 'win32' else ['/O2'],
        language='c++',
    )
]

# Cythonize if available
if CYTHON_AVAILABLE:
    extensions = cythonize(extensions)

setup(
    name='fileutils',
    version='1.1.0',
    author='Isaac Onagh',
    author_email='mkalafsaz@gmail.com',
    description='A comprehensive Python package for handling files and folders',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    ext_modules=extensions,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Cython',
    ],
    python_requires='>=3.9',
    install_requires=[
        'python-magic',
    ],
    setup_requires=(
        [
            'cython',
        ]
        if CYTHON_AVAILABLE
        else []
    ),
)
