#!/usr/bin/env python
# coding=utf-8

# DISCLAIMER: I am not sure this will work properly for everyone.
#             Please report bugs.

# Run this script to leverage the power of `distutils` to install or build.

# Doc :
# - https://docs.python.org/2/install/index.html
# - https://docs.python.org/2/distutils/setupscript.html

import io
from os import path
from setuptools import setup, find_packages

# Read version.py
__version__ = None
with io.open('VERSION') as f:
    exec(f.read())

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='galpak',
    version=__version__,
    author='Nicolas Bouché',
    author_email='nicolas.bouche@univ-lyon1.fr',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url='http://galpak3d.univ-lyon1.fr',
    license='GPL',
    description='A tool to extract the intrinsic (i.e. deconvolved) Galaxy '
                'Parameters and Kinematics from any 3-Dimensional data.',
    packages=find_packages('src', ),
    package_dir ={'': 'src'},
    python_requires='>=3.5',
    install_requires=['astropy>=2.0', 'numpy>=1.14', 'scipy', 'matplotlib>=2.0'],
)
