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
    name='SimplyNews',
    version='1.0',
    description="Python scrabing news from any news website",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='SimplyNews scrap news article with plain text and tags',
    author='Moon Faced Ltd.',
    author_email='info@moonfaced.co.uk',
    url='https://github.com/s4birli/SimplyNews',
    license='BSD',
    packages=find_packages('SimplyNews'),
    package_dir={'': 'SimplyNews'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
)
