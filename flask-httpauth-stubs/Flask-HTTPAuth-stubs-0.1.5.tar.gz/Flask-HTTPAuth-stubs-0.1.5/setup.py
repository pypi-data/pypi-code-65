#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

# Core Library modules
import os

# Third party modules
from setuptools import setup


def find_stub_files():
    """
    This function is taken from the awesome sqlalchey-stubs:
    https://github.com/dropbox/sqlalchemy-stubs/blob/master/setup.py#L32

    It's licensed under Apache 2.0:
    https://github.com/dropbox/sqlalchemy-stubs/blob/master/LICENSE
    """
    result = []
    for root, dirs, files in os.walk("flask_httpauth-stubs"):
        for file in files:
            if file.endswith(".pyi"):
                if os.path.sep in root:
                    sub_root = root.split(os.path.sep, 1)[-1]
                    file = os.path.join(sub_root, file)
                result.append(file)
    return result


setup(
    name="Flask-HTTPAuth-stubs",
    install_requires=[
        "mypy>=0.720",
        "typing-extensions>=3.7.4",
        "Flask-HTTPAuth>=4.0.0",
    ],
    packages=["flask_httpauth-stubs"],
    package_data={"flask_httpauth-stubs": find_stub_files()},
)
