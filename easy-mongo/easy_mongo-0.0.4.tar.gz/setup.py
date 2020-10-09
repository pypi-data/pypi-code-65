#!/usr/bin/env python
# -*-coding:utf-8-*-
from setuptools import setup, find_packages

setup(
    name='easy_mongo',
    version='0.0.4',
    description=
    'easy to use mongo(kb)',
    long_description=open('README.rst', encoding='utf-8').read(),
    author='ksust',
    author_email='admin@ksust.com',
    maintainer='ksust',
    maintainer_email='admin@ksust.com',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/ksust/easy_mongo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'pymongo==3.10.1',
        'PyYAML==5.3.1',
    ]
)
