from .config_loader import *
from .errors import *
from .extensions import *
from .inspect_tools import *
from .logging import *
from .re_dict import *
from .subrequest_classes import *
from .types import *

@property
def re_type():
    from typing import Pattern
    from warnings import warn
    warn("'re_type' is going to be deprecated. Use Pattern[str] instead", DeprecationWarning, 2)
    return Pattern[str]

__all__ = \
[
    're_type',
]
__pdoc__ = { }
__pdoc_extras__ = [ ]

submodules = \
[
    config_loader,
    errors,
    extensions,
    inspect_tools,
    logging,
    re_dict,
    subrequest_classes,
    types,
]

for _m in submodules: __all__.extend(_m.__all__)
from http_server_base.tools.docs import create_documentation_index
create_documentation_index(submodules, __name__, __pdoc__, __pdoc_extras__)
del create_documentation_index, submodules
