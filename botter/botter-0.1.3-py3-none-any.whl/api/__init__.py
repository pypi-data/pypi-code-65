"""
Main module of package, which implements core API.
"""

from .bot import *
from .bot_api import *
from .bot_base import *
from .bot_impl import *
from .errors import *

__all__ = [ ]
__pdoc__ = { }
__pdoc_extras__ = [ ]

submodules = \
[
    bot,
    bot_api,
    bot_base,
    bot_impl,
    errors,
]

for _m in submodules: __all__.extend(_m.__all__)
from botter.util import create_documentation_index
create_documentation_index(submodules, __name__, __pdoc__, __pdoc_extras__)
del create_documentation_index, submodules
