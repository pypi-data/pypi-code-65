class AiodagpiException(Exception):
    pass

class InvalidToken(AiodagpiException):
    """Raised when token is invalid
    """
    def __init__(self, error='Improper or invalid token passed.'):
        self.error = error
    def __str__(self):
        return self.error
