from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='dh',
    version='3.1.9',
    author='Isaac Onagh',
    author_email='mkalafsaz@gmail.com',
    description='A short description of your package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your-package',
    packages=find_packages(),
)
