#!/usr/bin/env python
"""The setup script."""
import os
import sys
from setuptools import setup, find_packages

if sys.version_info[0] < 3:
    with open('README.md') as f:
        long_description = f.read()
else:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join('pypdxapi', '__version__.py')) as f:
    exec(f.read(), version)

setup(
    name="pypdxapi",
    version=version['__version__'],
    author="Hallen Maia",
    author_email="hallenmaia@me.com",
    description="Python package for Paradox Modules",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/hallenmaia/pypdxapi/",
    # packages=find_packages(include=["pypdxapi"]),
    packages=find_packages(),
    test_suite="tests",
    install_requires=list(val.strip() for val in open("requirements.txt")),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["api", "client", "paradox", "camera"],
    license="MIT license",
)
