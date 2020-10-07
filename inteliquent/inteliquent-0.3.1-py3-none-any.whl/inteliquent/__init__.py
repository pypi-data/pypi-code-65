import logging

from .client import InteliquentClient
from .messaging import InteliquentMessaging


__author__ = "Inteliquent"
__version__ = "0.3.1"


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


log = logging.getLogger("inteliquent")
log.addHandler(NullHandler())


__all__ = ["InteliquentClient", "InteliquentMessaging"]
