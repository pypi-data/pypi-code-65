import setuptools

from glob import glob
from os.path import basename, splitext

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="firestore-operators",
    version="0.0.4",
    author="Cezar Azevedo de Faveri",
    author_email="cazevedodefaveri@gmail.com",
    description="Operator to send data to Firestore from Airflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/properati/firestore_operator",
    packages=setuptools.find_packages(),
    py_modules=['firestore_operators'],
    python_requires='>=3.6'
)
