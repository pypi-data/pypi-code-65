"""
---------------------------------------------------------------------
lcex.py
---------------------------------------------------------------------
This module defines custom exceptions used in LordCommander.

Version: 5.x
License: GNU General Public License 3
"""


class ProjectNotFoundException(Exception):
    """Project is not found."""
    pass


class NotAnAbsolutePathException(Exception):
    """Provided path is not an absolute path."""
    pass


class ArgumentNotProvidedException(Exception):
    """Necessary arguments are missing."""
    pass


class ActiveProjectNotSetException(Exception):
    """An active project is not set."""
    pass
