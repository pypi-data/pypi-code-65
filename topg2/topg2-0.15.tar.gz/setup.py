#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 13:51:49 2020

@author: jcl
"""

from distutils.core import setup
setup(
  name = 'topg2',         # How you named your package folder (MyLib)
  packages = ['topg2'],   # Chose the same as "name"
  version = '0.15',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Dataframe methods to implement cursor copy to postgress.',   # Give a short description about your library
  author = 'Johnny Lichtenstein',                   # Type in your name
  author_email = 'johnlichtenstein@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/johnlichtenstein/topg2',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/johnlichtenstein/topg2/archive/v_015.tar.gz',    # I explain this later on
  keywords = ['Pandas', 'Postgres', 'fast'],   # Keywords that define your package best
  install_requires=['psycopg2', "pandas"],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'])
    
