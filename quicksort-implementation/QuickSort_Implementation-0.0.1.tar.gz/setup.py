from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'QuickSort_Implementation',
    description = 'Sorting a list of numbers with quicksort',
    long_description=long_description,
    packages = ['quicksort'],
    zip_safe = False,
    version = '0.0.1',
    author = 'Shashank Saurav',
    author_emal = 'shashank.saurav@mail.utoronto.ca',
    license = 'MIT')
