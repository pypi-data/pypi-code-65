#!/usr/bin/env python
# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

# this package
from __pkginfo__ import *  # pylint: disable=wildcard-import



setup(
		description="Custom JSON Encoder for Python utilising functools.singledispatch to support custom encoders for both Python's built-in classes and user-created classes, without as much legwork.",
		extras_require=extras_require,
		install_requires=install_requires,
		py_modules=[],
		version=__version__,

		)
