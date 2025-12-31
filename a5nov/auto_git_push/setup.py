# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from setuptools import setup, find_packages

setup(
    name='auto_git_push',
    version='0.1.6',
    author='Isaac Onagh',
    author_email='mkalafsaz@gmail.com',
    description='auto git push',
    url='https://github.com/isaac4ever/auto_git_push',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gpush=auto_git_push.__main__:main',
        ],
    },
    #    dependencies={"black","pre-commit"},
)
