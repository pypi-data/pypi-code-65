"""
Provide errors for BaseRecognizer interface.
"""


class ValidationDataError(Exception):
    """
    Recognize data contains invalid characters or does not match the shape length error.
    """

    def __init__(self, message):
        self.message = message
