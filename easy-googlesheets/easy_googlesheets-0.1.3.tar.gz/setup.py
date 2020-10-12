#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 01:01:32 2020

@author: roberto
"""

from setuptools import setup, find_packages
import os

if os.path.exists('README.md'):
    with open('README.md') as readme_rst_file:
        long_description = readme_rst_file.read()

else:
    long_description = 'No description'


s = setup(
    install_requires=[
        'google-api-python-client',
        'google'
    ],
    classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    ],
    name='easy_googlesheets',
    version='0.1.3',
    description='Google sheets API, easy to use',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords = ['api', 'google', 'easy', 'sheets', 'database', 'googlesheets', 'free'],
    license='MIT',
    author='Roberto Lama Rodriguez',
    author_email='roberlama@gmail.com',
    url='https://github.com/RoberWare/easy_googlesheets',
    packages=find_packages(),
    entry_points={}
)
