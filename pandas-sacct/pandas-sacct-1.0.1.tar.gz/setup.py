#!/usr/bin/env python

import sys
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

version = {}
with open("sacct/version.py", "r") as stream:
    exec(stream.read(), version)
    
setup(
    name="pandas-sacct",
    version=version["__version__"],
    author="Brandon Cook",
    author_email="bgcook@lbl.gov",
    description="Read Slurm sacct as pandas dataframes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/NERSC/pandas-sacct",    
    install_requires=['pandas'],
    packages=['sacct'],
    python_requires=">=3.6",
)
