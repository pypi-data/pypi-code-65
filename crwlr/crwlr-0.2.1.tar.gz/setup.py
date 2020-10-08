#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

readme = ''
with open('README.md') as f:
    long_description = f.read()

license = ''
with open('LICENSE') as f:
    license = f.read()

setup(
    name='crwlr',
    version='0.2.1',
    description='Data Mining artifact for publication dbs',
    long_description='',
    author='Nico H.',
    author_email='e1129267@student.tuwien.ac.at',
    url='',
    license='',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['certifi==2020.4.5.1',
'chardet==3.0.4',
'configparser==5.0.0',
'crossref-commons==0.0.7',
'entrypoints==0.3',
'idna==2.9',
'lxml==4.5.0',
'mysqlclient==1.4.6',
'numpy==1.18.4',
'pandas==1.0.3',
'pybliometrics==2.4.0',
'python-dateutil==2.8.1',
'pytz==2020.1',
'ratelimit==2.2.1',
'requests==2.23.0',
'rispy==0.5.0',
'simplejson==3.17.0',
'six==1.14.0',
'SQLAlchemy==1.3.16',
'urllib3==1.25.9',
'xmltodict==0.12.0'],
    entry_points={
        'console_scripts': ['crwlr=crwlr.command_line:main'],
    },
    python_requires='>=3.6',
)
