class Error(Exception):
    """Base exception class for other exceptions."""
    pass


class LogTypeError(Error):
    """Error raised when an inavlid log type is passed to log()."""
    def __init__(self, logtype, message="Not a valid log type."):
        self.logtype = logtype
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.logtype} --> {self.message}'


class FormatGridError(Error):
    """Error raised when there's an error formatting a template grid."""
    pass