#! /usr/bin/python3.7.6

from setuptools import setup
from simplysql import __author__, __author_email__, __description__, __name__, __version__, __url__


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name=__name__,
      packages=["simplysql"],
      version=__version__,
      license="MIT",
      description=__description__,
      long_description=long_description,
      long_description_content_type="text/markdown",
      author=__author__,
      author_email=__author_email__,
      url=__url__,
      python_requires=">=3.7",
      download_url="https://github.com/Luanee/SimplySQL/archive/v0.1.0.tar.gz",
      keywords=["sql", "easy", "queries", "databases", "sqlite3"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License",
                   # TODO: Check compatibility
                   # "Programming Language :: Python :: 3",
                   # "Programming Language :: Python :: 3.4",
                   # "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.7"],
      )
