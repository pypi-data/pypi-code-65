class Error(BaseException):
    """Tokko Location service error"""

    def __init__(self, err_message: str = None):
        super().__init__(". ".join([
            self.__doc__,
            f"{err_message or ''}"
        ]))


class MethodCallError(Error):
    """API method error"""


class UnsupportedClassError(Error):
    """DataClass is required error"""


class APIConnectionError(Error):
    """API Connection error"""


class DataNotFoundError(Error):
    """Data not found error"""

