from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='intelix',
      version='0.1.2',
      description='Sophos Labs Intelix Client',
      author='Stephen O''Leary',
      author_email='stephen.oleary@sophos.com',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages())
