# -*- coding: utf-8 -*-
"""
Create Time: 2020/10/6 21:35
Author: mh
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGELOG.md')) as f:
    CHANGES = f.read()

requires = [
    'pandas',
    'numpy',
]


setup(
    author='MaHe',
    author_email='1692303843@qq.com',
    name='oilduction',
    version='0.1.0',
    description='Python package for Petroleum Engineers',
    long_description=README,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    url='https://github.com/mmmahhhhe/oilduction',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)