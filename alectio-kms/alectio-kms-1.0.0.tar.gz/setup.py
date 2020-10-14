#!/usr/bin/env python
"""
alectio-kms
==========
.. code:: shell
  $ sudo alectio-kms
"""

from setuptools import find_packages, setup

install_requires = ["jinja2", "flask", "requests"]
tests_requires = ["pytest", "flake8"]

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="alectio-kms",
    version="1.0.0",
    author="Devi Prasad Tripathy",
    author_email="devi.tripathy@alectio.com",
    url="https://github.com/",
    description="A CLI interface to get AlectioSDK token",
    long_description="A CLI interface to get AlectioSDK token",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    license="BSD",
    install_requires=install_requires,
    extras_require={
        "yaml": install_requires + ["pyyaml"],
        "toml": install_requires + ["toml"],
        "xml": install_requires + ["xmltodict"],
        "tests": install_requires + tests_requires,
    },
    tests_require=tests_requires,
    include_package_data=True,
    entry_points={"console_scripts": ["alectio-kms = alectiokmscli:main"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
)