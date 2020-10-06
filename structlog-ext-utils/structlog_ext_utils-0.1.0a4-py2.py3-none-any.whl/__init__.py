from contextlib import suppress

from structlog_ext_utils.__version__ import __version__

with suppress(ModuleNotFoundError):
    from structlog_ext_utils import processors
