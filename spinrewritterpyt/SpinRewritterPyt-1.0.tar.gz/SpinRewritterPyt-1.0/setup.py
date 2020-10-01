# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = \
    read('README.md')

setup(
    name='SpinRewritterPyt',
    version='1.0',
    description="Python bindings for SpinRewriter API",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='API spinner SpinRewriter',
    author='Moon Faced Ltd.',
    author_email='info@moonfaced.co.uk',
    url='http://www.moonfaced.co.uk',
    license='BSD',
    packages=find_packages('SpinRewriterPyt'),
    package_dir={'': 'SpinRewriterPyt'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
)
