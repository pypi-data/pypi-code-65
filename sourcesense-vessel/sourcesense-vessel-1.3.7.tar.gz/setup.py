#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2017 by Lev Lazinskiy
:license: MIT, see LICENSE for more details.
"""

import setuptools
from vessel.version import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sourcesense-vessel",
    version=VERSION,
    author="Sourcesense spa",
    author_email="open@sourcesense.com",
    description="Vessel Cli Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sourcesense.com",
    license="all rights reserved",
    packages=setuptools.find_packages(),
    include_package_data=True,
    scripts=['bin/vessel-cli'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: Other/Proprietary License",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
          'click',
          'pyfiglet',
          'cryptography',
          'requests',
          'hvac',
          'kubernetes',
          'jinja2'
      ],
    python_requires='>=3.6',
)