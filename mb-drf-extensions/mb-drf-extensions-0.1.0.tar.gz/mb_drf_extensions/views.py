from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import (
    exceptions,
    views,
)
from .exceptions import (
    ErrorMeta,
    Error,
    InternalServerError,
)
from .mixins import AtomicMixin


def exception_handler(exc, _context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        # swap exception
        exc_cls = ErrorMeta.errors_4_swapping.get(exc.__class__)
        exc_cls = exc_cls or InternalServerError
        exc = exc_cls(exc.detail)

    if isinstance(exc, Error):
        headers = {}

        exec_auth_header = getattr(exc, 'auth_header', None)
        if exec_auth_header:
            headers['WWW-Authenticate'] = exec_auth_header

        exec_wait = getattr(exc, 'wait', None)
        if exec_wait:
            headers['Retry-After'] = '%d' % exec_wait

        views.set_rollback()

        return exc.get_response(headers=headers)

    return None


class APIView(
    AtomicMixin,
    views.APIView,
):
    pass
