# Copyright 2020 John Lenton
# Licensed under GPLv3, see LICENSE file for details.

from setuptools import setup
from pathlib import Path

import geringoso

setup(
    name="geringoso",
    version=geringoso.__version__,
    author="John Lenton",
    author_email="jlenton@gmail.com",
    description="A Spanish to Geringoso library and filter",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/chipaca/geringoso",
    license="GPLv3",
    py_modules=["geringoso"],
    entry_points={
        "console_scripts": ["geringoso = geringoso:main"],
    },
    python_requires=">=3",
    install_requires=Path("requirements.txt").read_text().split(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Filters",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
