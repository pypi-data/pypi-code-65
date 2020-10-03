#!/usr/bin/env python

"""The setup script."""

from typing import List

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements: List[str] = []

setup_requirements: List[str] = [
    "pytest-runner",
]

test_requirements: List[str] = [
    "pytest>=3.7",
]

setup(
    author="Wink Saville",
    author_email="wink@saville.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Generate helixes that can optionally taper to a point at each end.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="taperable_helix",
    name="taperable_helix",
    packages=find_packages(include=["taperable_helix"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/winksaville/py-taperable-helix",
    version="0.8.5",
    zip_safe=False,
)
