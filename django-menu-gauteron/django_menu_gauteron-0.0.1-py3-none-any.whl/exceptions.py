class ConflictingArgumentException(Exception):
    """
    This exception is intended to be raised when conflicting
    parameters are defined simultaneously.
    """
    pass


class InvalidParameterTypeException(Exception):
    """
    This exception is intended to be raised when a
    parameter has not an expected type.
    """
    pass


class MissingArgumentException(Exception):
    """
    This exception is intended to be raised when a
    mandatory argument is missing.
    """
    pass


class MissingSettingException(Exception):
    """
    This exception is intended to be raised when a
    mandatory setting is missing.
    """
    pass
