#    _________             .__
#   /   _____/____    _____|  |__ _____
#   \_____  \\__  \  /  ___/  |  \\__  \
#   /        \/ __ \_\___ \|   Y  \/ __ \_
#  /_______  (____  /____  >___|  (____  /
#          \/     \/     \/     \/     \/
#    _________       _____  __
#   /   _____/ _____/ ____\/  |_
#   \_____  \ /  _ \   __\\   __\
#   /        (  <_> )  |   |  |
#  /_______  /\____/|__|   |__|
#          \/
#  Copyright (c) 2020.

"""
all user data are convert to base64
"""

__all__ = ['User']

import base64
import binascii

from py_singleton import singleton


def _is_base64(string):
    """check if data are base 64"""
    try:
        return base64.b64encode(base64.b64decode(string)) == string
    except binascii.Error:
        return False


@singleton
class User:
    """
    LoggerPackage manager, connection all loggers with package logging.
    Handles all logger files
    """
    __user64 = bytes

    def __init__(self):  # pylint: disable=W0221
        self.__user64 = bytes

    def save(self, value):
        """
        function for saving of value
        """
        self.user64 = value
        return self.user64

    def __str__(self):
        """
        return decode user64 to string
        """
        # noinspection PyArgumentList
        return self.user64.decode()

    def decode(self):
        """
        getter for user
        """
        return base64.b64decode(self.user64).decode()

    @property
    def user64(self):
        """save base64 user data"""
        return self.__user64

    @user64.setter
    def user64(self, value):
        if _is_base64(value) or isinstance(value, bytes):
            self.__user64 = value
            return
        self.__user64 = base64.b64encode(value.encode('ascii'))
