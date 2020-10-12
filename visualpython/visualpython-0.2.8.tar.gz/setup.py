# coding: utf-8
import os
#from distutils.core import setup
#from distutils.command.build_py import build_py
#from distutils.command.sdist import sdist
#from os.path import join as pjoin

from setuptools import setup, find_packages

name = 'visualpython'

setup(
    name             = name,
    version          = '0.2.8',
    packages         = find_packages(),
    package_data     = {"": ["*"], 'visualpython' : ['vp.yaml', 'README.md']},
    #package_data     = {"blackpen": ["*"]},
    scripts          = ['visualpython/bin/visualpy', 'visualpython/bin/visualpy.bat'],
    description      = 'visualpython',
    author           = 'BlackLogic',
    author_email     = 'blacklogic.dev@gmail.com',
    url              = 'https://bl-vp.blogspot.com/',
    license          = 'BSL v1.1',
    install_requires = [],
    platforms        = "Linux, Mac OS X, Windows",
    keywords         = ['Visual', 'visual', 'BlackPen', 'visualpython', 'blackpen', 'BlackPen', 'black', 'Black'],
    python_requires  = '>=3.6',
    )
