#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup  # noqa, analysis:ignore
except ImportError:
    print ('''please install setuptools
python -m pip install setuptools
or
python -m pip install setuptools''')
    raise ImportError()

setup(name='PyjQuery',
      version='2.3.4',
      description = 'Write Less, Do More',
      py_modules=['jquery'],
      scripts=['jquery.py'],
      license='MIT',
      platforms='any'
      )
