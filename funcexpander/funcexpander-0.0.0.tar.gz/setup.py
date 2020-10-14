from setuptools import find_packages
from distutils.core import setup


setup(name='funcexpander',
      long_description=open("./README.txt").read() +
      "\n\n" + open("./CHANGELOG.txt").read(),
      license="MIT",
      author='Ahmed Reda Hbaiz',
      author_email='reda.hbaiiz@gmail.com',
      keywords="expander",
      packages=find_packages(),
      
      )
