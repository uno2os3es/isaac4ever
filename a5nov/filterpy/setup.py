# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        'cy_heu.pyx', compiler_directives={'language_level': '3'}
    )
)
