#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='diagnes-comandos',
    version='1.0.3',
    description='Pluggable django app for managing commands',
    author='Diagnes',
    author_email='anderson.bispo@gmail.com',
    url='https://bitbucket.org/diagnes/diagnes-comandos',
    license='MIT',

    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    include_package_data=True,
    zip_safe=False,
)