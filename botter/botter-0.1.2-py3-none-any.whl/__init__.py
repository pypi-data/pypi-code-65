"""
.. include:: ../../README.md
"""

from collections import namedtuple

__title__ = 'botter'
__author__ = 'Peter Zaitcev / USSX Hares'
__license__ = 'BSD 2-clause'
__copyright__ = 'Copyright 2019 Peter Zaitcev'
__version__ = '0.1.2'

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(*__version__.split('.'), releaselevel='alpha', serial=0)

from .api import *

__all__ = \
[
    'version_info',
    '__title__',
    '__author__',
    '__license__',
    '__copyright__',
    '__version__',
]
__pdoc__ = { }
__pdoc_extras__ = [ ]

submodules = \
[
    api,
]

for _m in submodules: __all__.extend(_m.__all__)
from botter.util import create_documentation_index
create_documentation_index(submodules, __name__, __pdoc__, __pdoc_extras__)
del create_documentation_index, submodules
