import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()


setup(
    name="greble-flow",
    version="0.0.3.5",
    packages=find_packages(exclude=("tests", "example")),
    description="Greble flow",
    long_description=README,
    author="Greble",
    author_email="info@greble.io",
    url="https://github.com/greble/python-flow-helper",
    install_requires=["greble-flow>=0.0.1", "click", "flask"],
)
