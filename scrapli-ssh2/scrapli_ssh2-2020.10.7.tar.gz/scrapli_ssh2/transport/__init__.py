"""scrapli_ssh2.transport"""
from scrapli_ssh2.transport.cssh2 import SSH2_TRANSPORT_ARGS as TRANSPORT_ARGS
from scrapli_ssh2.transport.cssh2 import SSH2Transport as Transport

__all__ = (
    "Transport",
    "TRANSPORT_ARGS",
)
