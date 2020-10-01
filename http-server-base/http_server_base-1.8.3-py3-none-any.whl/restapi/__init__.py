from .extras import *
from .rest_request_handler import *
from .rest_router import *

simple_return = RestRouter.simple_return
encode_result = RestRouter.encode_result
rest_method = RestRouter.rest_method
extract_args = RestRouter.extract_args

__all__ = \
[
    'encode_result',
    'extract_args',
    'rest_method',
    'simple_return',
]
__pdoc__ = { }
__pdoc_extras__ = [ ]

submodules = \
[
    extras,
    rest_request_handler,
    rest_router,
]

for _m in submodules: __all__.extend(_m.__all__)
from http_server_base.tools.docs import create_documentation_index
create_documentation_index(submodules, __name__, __pdoc__, __pdoc_extras__)
del create_documentation_index, submodules
