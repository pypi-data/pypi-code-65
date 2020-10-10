#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    reshapedata LLC
"""
import platform
from setuptools import setup
from setuptools import find_packages

setup(
    name = 'pykdc',
    version = '1.5.0',
    install_requires=[
        'requests',
    ],
    packages=find_packages(),
    license = 'Apache License',
    author = 'Reshapedata',
    author_email = 'hulilei@takewiki.com.cn',
    url = 'http://www.reshapedata.com',
    description = 'reshape kdc webapi in py language ',
    keywords = ['reshapedata', 'pykdc','kdcapi'],
    python_requires='>=3.6',
)
