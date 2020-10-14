
class MellisugaError(Exception):
    pass


class MellisugaViewError(MellisugaError):
    STATUS_CODE = 500

    def __init__(self, msg=''):
        super(MellisugaViewError, self).__init__(
            self.__class__.__name__ + ': %s' % msg)


class BadRequestError(MellisugaViewError):
    STATUS_CODE = 400


class UnauthorizedError(MellisugaViewError):
    STATUS_CODE = 401


class ForbiddenError(MellisugaViewError):
    STATUS_CODE = 403


class NotFoundError(MellisugaViewError):
    STATUS_CODE = 404


class MethodNotAllowedError(MellisugaViewError):
    STATUS_CODE = 405


class RequestTimeoutError(MellisugaViewError):
    STATUS_CODE = 408


class ConflictError(MellisugaViewError):
    STATUS_CODE = 409


class UnprocessableEntityError(MellisugaViewError):
    STATUS_CODE = 422


class TooManyRequestsError(MellisugaViewError):
    STATUS_CODE = 429


ALL_ERRORS = [
    MellisugaViewError,
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    RequestTimeoutError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError
]
