#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2012 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
"""
Package just the inkex module itself
"""

from setuptools import setup

setup(
    name='inkex',
    version='1.0.1',
    description='Inkscape Extensions Library',
    long_description='This module provides support for inkscape extensions, it includes support for opening svg files and processing them',
    author='Inkscape Authors',
    url='https://gitlab.com/inkscape/extensions',
    author_email='devel@lists.inkscape.org',
    platforms='linux',
    license='GPLv2',
    packages=['inkex', 'inkex.elements', 'inkex.tester'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=['lxml'],
)
