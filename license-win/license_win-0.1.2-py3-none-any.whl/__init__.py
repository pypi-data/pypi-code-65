"""
.. include:: ../README.rst
"""

from collections import namedtuple

__title__ = 'license-win'
__author__ = 'Peter Zaitcev / USSX Hares'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Peter Zaitcev'
__version__ = '0.1.2'

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(*__version__.split('.'), releaselevel='alpha', serial=0)

from .core import *

autoregister()
