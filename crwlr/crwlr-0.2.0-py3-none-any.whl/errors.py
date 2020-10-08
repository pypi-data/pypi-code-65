#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        self.message = message


class ExtractError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        super().__init__(message)


class ConfigAttributeMissingError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        super().__init__(message)


class ConfigSectionMissingError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        super().__init__(message)
