#!/usr/bin/env python

import os
import sys
import setuptools

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='pytryfi',
      version='v0.0.1',
      packages=[ 'pytryfi' ],
      description='Python Interface for TryFi Dog Collars',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/sbabcock23/pytryfi',
      author='Steve Babcock',
      author_email='steve.w.babcock@gmail.com',
      license='Apache Software License',
      install_requires=[ 'requests>=2.0' ],
      keywords=[ 'tryfi', 'try fi', 'dog collar' ], 
      zip_safe=True,
      classifiers=[ "Programming Language :: Python :: 3",
                    "License :: OSI Approved :: Apache Software License",
                    "Operating System :: OS Independent",
      ],
)
