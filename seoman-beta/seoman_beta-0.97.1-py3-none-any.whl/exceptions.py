class SeomanException(Exception):
    """
    Generic exception class for user-friendly errors for Seoman.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        class_name = self.__class__.__name__
        return f"{class_name}: {self.message}"


class BrokenFileError(SeomanException):
    def __init__(self, message):
        super().__init__(message)


class FolderNotFoundError(SeomanException):
    def __init__(self, message):
        super().__init__(message)


class MissingParameterError(SeomanException):
    def __init__(self, message):
        super().__init__(message)
