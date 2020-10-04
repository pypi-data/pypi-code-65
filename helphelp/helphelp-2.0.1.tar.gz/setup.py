#!/usr/bin/env python

import pathlib as pl
from setuptools import setup, find_packages


readme = pl.Path("README.md").read_text(encoding="utf-8")
long_description = readme[:readme.index("---")]


setup(
    name="helphelp",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["pyh = helphelp:main"]
    },
    version="2.0.1",
    description="man-like tool to get online help on Python modules, classes and functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Benoit Hamelin",
    author_email="benoit@benoithamelin.com",
    url="https://github.com/hamelin/helphelp/",
    install_requires=["nestedtext"]
)
