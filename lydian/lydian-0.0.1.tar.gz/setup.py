#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = {}
with open("lydian/__init__.py") as fp:
    exec(fp.read(), version)


setuptools.setup(
    name="lydian",
    version=version['__version__'],
    author="Vipin Sharma",
    author_email="sh.vipin@gmail.com",
    description="Traffic generation, system validation and monitoring at very large scale.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitvipin/grus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
)
