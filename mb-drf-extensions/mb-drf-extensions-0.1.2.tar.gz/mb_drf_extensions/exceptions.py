from rest_framework import (
    exceptions,
    status,
    response,
)
from .settings import MB_EXCEPTIONS

ERROR_CODE_NAME = MB_EXCEPTIONS.get(
    'ERROR_CODE_NAME', 'error')
ERROR_MESSAGE_NAME = MB_EXCEPTIONS.get(
    'ERROR_MESSAGE_NAME', 'error_description')


class ErrorMeta(type):
    """
    meta class of errors
    """

    errors = {}
    errors_4_swapping = {}

    def __new__(mcs, class_name, class_bases, class_attr):
        cls = super().__new__(mcs, class_name, class_bases, class_attr)
        if class_name == 'Error':
            return cls

        error_code = getattr(cls, 'error_code', None)
        assert error_code, (
            'error_code is not specified in error class {}'.format(
                class_name)
        )
        assert error_code not in mcs.errors, (
            'duplicated error_code {} found'.format(error_code))

        mcs.errors[error_code] = cls
        swap = getattr(cls, 'swap', None)
        if swap and issubclass(swap, exceptions.APIException):
            mcs.errors_4_swapping[swap] = cls

        return cls


class Error(Exception, metaclass=ErrorMeta):
    """
    base class of errors
    """

    status_code = None
    error_code = None
    error_message = None

    def __init__(self, error_message=None):
        if error_message:
            self.error_message = error_message

    def get_data(self, data=None):
        resp = {
            ERROR_CODE_NAME: self.error_code,
            ERROR_MESSAGE_NAME: self.error_message,
        }
        if isinstance(data, dict):
            resp.update(data)
        elif isinstance(data, (list, tuple)):
            resp.update(results=data)

        return resp

    def get_response(self, data=None, headers=None):
        return response.Response(
            data=self.get_data(data),
            headers=headers,
            status=self.status_code,
        )


class Success(Error):
    """
    this is the special class for http status_code: 200.
    """

    status_code = status.HTTP_200_OK
    error_code = 2000
    error_message = 'success'


class CreatedSuccess(Error):
    status_code = status.HTTP_201_CREATED
    error_code = 2010
    error_message = 'success'


class DestroyedSuccess(Error):
    status_code = status.HTTP_204_NO_CONTENT
    error_code = 2040
    error_message = 'success'


class BadRequestError(Error):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 4000
    error_message = 'bad request'
    swap = exceptions.ValidationError


class UnauthorizedError(Error):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 4010
    error_message = 'unauthorized'
    swap = exceptions.NotAuthenticated


class AuthorizeFailedError(Error):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 4011
    error_message = 'authorize failed'
    swap = exceptions.AuthenticationFailed


class PermissionDeniedError(Error):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 4030
    error_message = 'permission denied'
    swap = exceptions.PermissionDenied


class NotFoundError(Error):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 4040
    error_message = 'not found'
    swap = exceptions.NotFound


class MethodNotAllowedError(Error):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    error_code = 4050
    error_message = 'method not allowed'
    swap = exceptions.MethodNotAllowed


class NotAcceptableError(Error):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    error_code = 4060
    error_message = 'not acceptable'
    swap = exceptions.NotAcceptable


class ConflictError(Error):
    status_code = status.HTTP_409_CONFLICT
    error_code = 4090
    error_message = 'data conflict occurred'


class UnsupportedMediaTypeError(Error):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    error_code = 4150
    error_message = 'media type not supported'
    swap = exceptions.UnsupportedMediaType


class TooManyRequestsError(Error):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = 4290
    error_message = 'too many requests'
    swap = exceptions.Throttled


class InternalServerError(Error):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 5000
    error_message = 'internal server error'
    swap = exceptions.APIException


class InternalRPCError(Error):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 5001
    error_message = 'internal RPC error'
