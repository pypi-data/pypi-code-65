"""Package level exceptions"""


class AuthenticationError(Exception):
    """Authentication Failed"""


class SessionExpiredError(Exception):
    """Session has expired"""
