#!/usr/bin/env python
from setuptools import setup

setup(
    name="helsingborgalarm",
    version="1.0",
    description="Get alarms from Helsingborg Stad",
    author="Jonas Björk",
    author_email="jonas.bjork@gmail.com",
    license="MIT",
    keywords="alarm helsingborg hbg",
    url="https://github.com/jonasbjork/helsingborgalarm",
    packages=[
        "helsingborgalarm",
    ],
    python_requires=">=3.4",
    tests_require=[
        "pytest==6.1.1"
    ]
)
