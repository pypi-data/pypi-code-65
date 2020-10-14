#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='lazyRecursion',
      version='0.1',
      author='Felix Benning',
      author_email='felix.benning@gmail.com',
      description='lazy RecursiveSequence with optional caching',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/FelixBenning/lazyConfig',
      py_modules=['lazyRecursion'],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
            "Development Status :: 4 - Beta"
      ],
      python_requires='>=3.8',
     )