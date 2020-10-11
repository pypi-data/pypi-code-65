# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

if os.path.isfile("./README.md"):
    with open("./README.md") as f:
        readme = f.read()
else:
    readme = ""

if os.path.isfile("./requirements.txt"):
    requires = []
    with open("./requirements.txt") as lines:
        for line in lines:
            requires.append(line.strip())
else:
    requires = []

setup(
    name="estimator-wrapper",
    version="1.0",
    license="MIT",
    description="Estimator Wrapper",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Wu Wenmin",
    author_email="wuwenmin1991@gmail.com",
    packages=find_packages("./"),
    install_requires=requires,
)
