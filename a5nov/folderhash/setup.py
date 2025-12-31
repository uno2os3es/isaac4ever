# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Simple compiler flags that work everywhere
extra_compile_args = ['-O2']
extra_link_args = []

extensions = [
    Extension(
        'folder_hash',
        sources=['folder_hash.pyx'],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name='folder_hash',
    version='1.0.0',
    description='Fast folder hashing C extension',
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': '3',
            'boundscheck': False,
            'wraparound': False,
            'initializedcheck': False,
            'nonecheck': False,
        },
    ),
    zip_safe=False,
)
