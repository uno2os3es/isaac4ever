# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup, find_packages

setup(
    name='wget2',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'wget2=wget2.cli:main',
        ],
    },
    author='Isaac4ever',
    description='Multi-threaded Python-based wget alternative',
    url='https://github.com/isaac4ever/wget2',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
