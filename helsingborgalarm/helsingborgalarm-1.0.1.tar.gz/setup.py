#!/usr/bin/env python
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="helsingborgalarm",
    version="1.0.1",
    description="Get alarms from Helsingborg Stad",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jonas Björk",
    author_email="jonas.bjork@gmail.com",
    license="MIT",
    keywords="alarm helsingborg hbg",
    url="https://github.com/jonasbjork/helsingborgalarm",
    packages=[
        "helsingborgalarm",
    ],
    python_requires=">=3.5",
    tests_require=[
        "pytest==6.1.1"
    ]
)
