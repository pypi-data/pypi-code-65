#!/usr/bin/env python
# -*- coding: utf-8 -*-

'The setup script.'

# import setuptools
from distutils.core import setup
from setuptools import find_packages
import io
import os, platform
from os import path as op

with open('README.md', 'r') as readme_file:
    readme = readme_file.read()


here = op.abspath(op.dirname(__file__))

# get the dependencies and installs
with io.open(op.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]

dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='dingpy',
    version='1.0.2',
    author='Tina Bu',
    author_email='tina.hongbu@gmail.com',
    description='first release :)',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/tinahbu/dingpy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
    install_requires=install_requires,
    dependency_links=dependency_links,
    license='MIT license',
    include_package_data=True,
    package_data={'dingpy': ['data/*.mp3']},
    keywords=['notification', 'alarm', 'alert'],
    packages=find_packages(include=['dingpy']),
    zip_safe=True
)


