"""Common RBX exceptions."""


class FatalException(Exception):
    """Raise this exception for non-transient errors.

    These exceptions can be given an extra details object, which may be used by the caller to log
    this as extra information.
    """
    message = 'Something went wrong!'

    def __init__(self, message=None, details=None):
        super().__init__(message or self.message)
        self.details = details

    def to_dict(self):
        rv = {
            'message': str(self)
        }

        if self.details:
            rv['details'] = self.details

        return rv


class HTTPException(FatalException):
    """A FatalException with an HTTP status code and a URL."""
    def __init__(self, message, status_code=400, url=None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.url = url

    def to_dict(self):
        rv = super().to_dict()
        if self.url:
            rv['url'] = self.url

        return rv


class BadRequest(HTTPException):
    """Convenience Exception to use from within a Flask service/blueprint.

    Raising this exception will be caught by the error handler and formatted as an HTTP response,
    using the provided status_code.
    """


class ClientException(HTTPException):
    """Raised from within the rbx.clients package, caused by third-party APIs."""


class TransientException(Exception):
    """Raise this exception when we know the cause is transient (e.g.: connection errors,
    consistency error, ...).
    """
