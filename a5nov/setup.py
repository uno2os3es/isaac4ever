# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r', encoding='utf-8') as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith('#')
    ]

setup(
    name='fh',
    version='0.1.7',
    author='Isaac Onagh',
    author_email='mkalafsaz@gmail.com',
    description='A short description of your package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your-package',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
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
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'isort',
            'flake8',
            'mypy',
            'pre-commit',
        ],
        'docs': [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinx-autodoc-typehints',
        ],
    },
    entry_points={
        'console_scripts': [
            'gpush=auto_git_push.__main__:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
