"""

Captivity main import. Imports all other captivity modules that do the actual work, and handles the flagging of issues.
To change captivity from exception to warning mode use `import captivity; captivity.warning_mode();` or
`captivity.exception_mode()` to go back.

"""


import warnings


def warning_mode():
    """

    Enable warning mode in captivity. Replaces exception mode, which is the default.
    In this mode, captivity raises a captivity.CaptivityWarning for each identified issue

    """
    global flag_issue
    flag_issue = raise_warning


def exception_mode():
    """

    Enables the default captivity mode, in which captivity raises a captivity.CaptivityException for identified issue

    :return:
    """
    global flag_issue
    flag_issue = raise_exception


class CaptivityException(Exception):
    pass


class CaptivityWarning(Warning):
    pass


def raise_exception(message: str):
    raise CaptivityException(message)


def raise_warning(message: str):
    warnings.warn(message, CaptivityWarning)


flag_issue = raise_exception

from captivity import merge
from captivity import concat
