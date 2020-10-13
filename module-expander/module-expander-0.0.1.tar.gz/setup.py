from setuptools import find_packages
from distutils.core import setup


classifiers = [
    "Developement status :: 5 - Production/Stable",
    "Intended"
]
setup(name='module-expander',
      version='0.0.1',
      long_description=open("./README.txt").read() +
      "\n\n" + open("./CHANGELOG.txt").read(),
      license="MIT",
      author='Ahmed Reda Hbaiz',
      author_email='reda.hbaiiz@gmail.com',
      keywords="expander",
      packages=find_packages(),
      )
