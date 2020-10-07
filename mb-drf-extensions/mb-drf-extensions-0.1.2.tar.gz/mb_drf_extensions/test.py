__all__ = [
    'APITestCase',
    'APISimpleTestCase',
    'APITransactionTestCase',
    'APILiveServerTestCase',
]

from uuid import uuid4
from rest_framework.test import (
    APITestCase,
    APISimpleTestCase,
    APITransactionTestCase,
    APILiveServerTestCase,
    testcases,
)
from .mocks import authentication_mock as _mock


def authentication_mock(**mock_kwargs):
    """

    :param mock_kwargs:
    :return:
    """
    access_token = mock_kwargs.setdefault(
        'access_token', uuid4().hex)

    def decorator(func):
        func = _mock(**mock_kwargs)(func)

        def wrapped(*args, **func_kwargs):
            assert len(args)
            instance = args[0]
            assert isinstance(instance, testcases.SimpleTestCase)
            instance.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
            return func(*args, **func_kwargs)

        return wrapped

    return decorator
