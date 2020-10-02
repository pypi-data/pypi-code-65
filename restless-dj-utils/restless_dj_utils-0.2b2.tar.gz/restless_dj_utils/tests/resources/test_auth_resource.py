import pytest

from django.contrib.auth import models

from restless_dj_utils.rest_sessions.models import APISession
from restless_dj_utils.resources.auth import AuthenticatedResourceMixin
from restless_dj_utils.tests.conftest import TEST_USERNAME, TEST_PASSWORD


REMOTE_ADDRESS = '192.168.1.1'
USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 ' \
             'Mobile Safari/537.36'


@pytest.mark.django_db(transaction=True)
def test_auth_resource_mixin(create_user, rf):
    """Test with valid token"""

    user, token = APISession.authenticate_user(
        TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT)

    resource = AuthenticatedResourceMixin()
    resource.request = rf.get('/', HTTP_AUTHORIZATION=token)

    assert resource.is_authenticated() is True
    assert resource.request.user == user


@pytest.mark.django_db(transaction=True)
def test_auth_resource_mixin_with_prefix(create_user, rf):
    """Test with a prefix"""

    user, token = APISession.authenticate_user(
        TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT)

    resource = AuthenticatedResourceMixin()
    resource.request = rf.get('/', HTTP_AUTHORIZATION=f'Bogus {token}')

    assert resource.is_authenticated() is True
    assert resource.request.user == user


@pytest.mark.django_db(transaction=True)
def test_auth_resource_mixin_invalid_token(rf):
    """Test with a prefix"""

    resource = AuthenticatedResourceMixin()
    resource.request = rf.get('/', HTTP_AUTHORIZATION='Bogus')

    assert resource.is_authenticated() is False
    assert resource.request.user == models.AnonymousUser()



@pytest.mark.django_db(transaction=True)
def test_auth_resource_mixin_no_header(rf):
    """Test with a prefix"""

    resource = AuthenticatedResourceMixin()
    resource.request = rf.get('/')

    assert resource.is_authenticated() is False
    assert resource.request.user == models.AnonymousUser()
