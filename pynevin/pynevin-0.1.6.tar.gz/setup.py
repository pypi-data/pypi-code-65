import pathlib
from setuptools import setup, find_packages
from pynevin.pypi import PyPi
from pynevin.cli import cli

HERE = pathlib.Path(__file__).parent

PACKAGE_NAME = 'pynevin'
VERSION = PyPi.get_latest_version(PACKAGE_NAME)
AUTHOR = 'Nevin WS Ganesan'
AUTHOR_EMAIL = 'PyNevin@idarkduck.com'
URL = 'https://github.com/iDuckDark/PyNevin'

LICENSE = 'Apache License 2.0'
DESCRIPTION = "Nevin's Python Packages: Algorithms, Utils, Leetcode & Helper functions"
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'click',
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      entry_points='''
            [console_scripts]
            pynevin=cli:cli
        ''',
      )
