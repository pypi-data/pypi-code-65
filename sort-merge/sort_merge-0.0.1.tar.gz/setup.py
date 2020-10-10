from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'sort_merge',
    description = 'Sorting a list of numbers with mergesort',
    long_description=long_description,
    packages = ['sort_merge'],
    zip_safe = False,
    version = '0.0.1',
    author = 'Shashank Saurav',
    author_emal = 'shashank.saurav@mail.utoronto.ca',
    license = 'MIT')
