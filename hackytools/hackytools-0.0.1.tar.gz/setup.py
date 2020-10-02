import re
from setuptools import find_packages, setup
from codecs import open
from os import path
HERE = path.abspath(path.dirname(__file__))
PACKAGE_NAME = 'hackytools'
with open(path.join(HERE, PACKAGE_NAME, "__init__.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

with open('README.md') as f:
    README = f.read()

setup(name=PACKAGE_NAME,
      version=VERSION,
      description="Tools that are hacky. Obviously.",
      long_description=README,
      long_description_content_type="text/markdown",
      author='Hackysack',
      author_email='tk13xr37@gmail.com',
      packages=find_packages(exclude=[]),
      python_requires='>=3.6',)
