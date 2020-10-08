# from distutils.core import setup


import os
from setuptools import setup, find_packages


path = os.path.abspath(os.path.dirname(__file__))

try:
  with open(os.path.join(path, 'README.md')) as f:
    long_description = f.read()
except Exception as e:
  long_description = "customize okta cli"

setup(
    name='sammaNLP',
    version='0.0.3',
    packages=find_packages(),
    license='MIT',
    author='samma',
    author_email='13336502700@163.com',
    description='a tool for nlp',
    install_requires = []
)