#!/usr/bin/env python

import errno
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from raise_3 import __doc__, __version__

project_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(project_directory, 'README.rst')

readme_file = open(readme_path)
try:
    long_description = readme_file.read()
finally:
    readme_file.close()


def bdist_wheel_args_check(_2_or_3, args=sys.argv):
    if 'bdist_wheel' not in args:
        return False
    tag = 'py' + str(_2_or_3)
    if '--python-tag' in args and tag in args:
        return True
    if ('--python-tag=' + tag) in args:
        return True
    return False


if 'sdist' in sys.argv:
    # When building a source distribution, include all versions:
    modules = ['raise_3', 'raise_2', 'raise_no_traceback']
else:
    # When not building a source distribution, we can include
    # just the file for the matching Python version.
    modules = ['raise_']

    packaged_path = os.path.join(project_directory, 'raise_.py')
    if bdist_wheel_args_check(3):
        source_path = os.path.join(project_directory, 'raise_3.py')
    elif bdist_wheel_args_check(2):
        source_path = os.path.join(project_directory, 'raise_2.py')
    elif sys.version_info >= (3,):
        source_path = os.path.join(project_directory, 'raise_3.py')
    else:
        source_path = os.path.join(project_directory, 'raise_2.py')
    try:
        os.unlink(packaged_path)
    except OSError as error:
        if error.errno != errno.ENOENT:
            raise
    os.link(source_path, packaged_path)

setup(
    name='raise',
    version=__version__,
    description=__doc__.split('\n')[0],
    long_description=long_description,
    license='0BSD',
    url='https://github.com/mentalisttraceur/python-raise',
    author='Alexander Kozhevnikov',
    author_email='mentalisttraceur@gmail.com',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
    ],
    py_modules=modules,
)
