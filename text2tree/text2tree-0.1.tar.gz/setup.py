#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name          = 'text2tree',
    version       = '0.1',
    license       = 'BSD 3-Clause License',
    description   = 'Description text',
    url           = 'https://github.com/tklijnsma/text2tree.git',
    author        = 'Thomas Klijnsma',
    author_email  = 'tklijnsm@gmail.com',
    py_modules    = ['text2tree'],
    zip_safe      = False,
    scripts       = ['bin/texhelp-toc'],
    )