#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from codecs import open
from os import path
from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


#with open(path.join('requirements.txt'), encoding='utf-8') as f:
#    requirements = [line.strip() for line in f if line]


setup_requirements = []

test_requirements = []

setup(
    author="Oriel Zambrano Vergara",
    author_email='oristides@gmail.com',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python package to check data quality just using ks tests",
    entry_points={
        'console_scripts': [
            'ksfest=ksfest.cli:main',
        ],
    },
    install_requires=['numpy>=1.15', 'seaborn', 'pandas>=0.19','scipy>=0.18','tqdm>=4.38.0','matplotlib==3.1.1', 'click>=7.0'],
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ksfest',
    name='ksfest',
    packages=find_packages(include=['ksfest', 'ksfest.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=['numpy>=1.15','seaborn', 'pandas>=0.19','scipy>=0.18','tqdm>=4.38.0','matplotlib==3.1.1', 'click>=7.0'],
    url='https://github.com/oristides/ksfest',
    download_url="https://github.com/oristides/ksfest/archive/0.1.21.tar.gz",
    version='0.1.21',
    zip_safe=False,
)
