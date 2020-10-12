import pathlib
from setuptools import setup,find_packages

# The directory containig the file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name="gsheetgraph",
version="0.1.0",
description="this is gsheetgraph package",
long_description=README,
long_description_content_type="text/markdown",
author="Neeraj Kumar",
author_email="neeraj.neerajkumar11@gmail.com",
license="MIT",
classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8"
],
packages=['gsheetgraph'],
include_package_data=True,
install_requires=[])