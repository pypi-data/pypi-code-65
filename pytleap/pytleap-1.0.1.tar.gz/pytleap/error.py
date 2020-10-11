"""Define errors and exceptions."""

from aiohttp import ClientError, ClientResponseError, ServerTimeoutError


class PytleapError(Exception):
    """Base error"""

    def __init__(self, message, cause=None):
        super().__init__()
        self.message = message
        self.cause = cause

    def __str__(self):
        if self.cause:
            return f"{self.message} ({self.cause})"
        return self.message


class CommunicationError(PytleapError):
    """Error when communicating with the EAP device."""


# pylint: disable=W0622
class TimeoutError(CommunicationError):
    """Error when there is a timeout"""


class AuthenticationError(PytleapError):
    """Error when itś impossible to authenticate (invalid/wrong credentials"""


class RequestError(PytleapError):
    """Error when the server returns an error"""


def convert_exception(message: str, err: ClientError) -> PytleapError:
    """Given a ClientError exception (from aiohttp), return the corresponding PytleapError."""
    if isinstance(err, ServerTimeoutError):
        return TimeoutError(message, err)
    if isinstance(err, ClientResponseError):
        if err.status in [401, 403]:
            return AuthenticationError(message, err)

    return CommunicationError(message)
