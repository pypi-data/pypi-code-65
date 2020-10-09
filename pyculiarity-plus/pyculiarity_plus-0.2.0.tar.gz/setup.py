#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: saiya.jiang@grabtaxi.com>
from distutils.core import setup
import setuptools

setup(
    name='pyculiarity_plus',
    version='0.2.0',
    description='seasonal anomaly detection',
    author='saiya.jiang',
    author_email='saiya.jiang@grabtaxi.com',
    url='',
    packages=setuptools.find_packages(),

    # 依赖包
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'statsmodels'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable ',
        'Operating System :: MacOS',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
