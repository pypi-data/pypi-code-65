import datetime
import pytest

from unittest import mock
from django.contrib.auth import get_user_model

from restless_dj_utils.rest_sessions.models import APISession
from restless_dj_utils.exceptions import AuthenticationError, SessionExpiredError
from restless_dj_utils.rest_sessions.conf import ACCESS_BACKEND, INACTIVITY_TIMEOUT
from restless_dj_utils.tests.conftest import TEST_USERNAME

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_authenticate_token(authenticate_user):
    """Test with valid token"""

    __, token = authenticate_user

    with mock.patch(f'{ACCESS_BACKEND}.log_session_access') as mlog_session_access:
        api_session, token_data = APISession.authenticate_token(token)

    assert api_session.user.username == TEST_USERNAME
    assert token_data == {
        'session_id': api_session.id,
        'user_id': api_session.user.id
    }
    mlog_session_access.assert_called_once_with(api_session, INACTIVITY_TIMEOUT, False)


@pytest.mark.django_db(transaction=True)
def test_authenticate_token_inactive_session(authenticate_user):
    """Test when session has be deactivated"""
    api_session, token = authenticate_user

    api_session.is_active = False
    api_session.save(update_fields=['is_active'])

    with mock.patch(f'{ACCESS_BACKEND}.log_session_access') as mlog_session_access:
        with pytest.raises(AuthenticationError):
            APISession.authenticate_token(token)

    mlog_session_access.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_authenticate_token_expired_session(authenticate_user):
    """Test when session has expired"""
    __, token = authenticate_user

    with mock.patch(f'{ACCESS_BACKEND}.log_session_access', side_effect=SessionExpiredError):
        with pytest.raises(AuthenticationError):
            APISession.authenticate_token(token)


@pytest.mark.django_db(transaction=True)
def test_authenticate_token_inactive_user(authenticate_user):
    """Test when user has been deactivated"""
    api_session, token = authenticate_user

    api_session.user.is_active = False
    api_session.user.save(update_fields=['is_active'])

    with pytest.raises(AuthenticationError):
        APISession.authenticate_token(token)


@pytest.mark.django_db(transaction=True)
def test_authenticate_token_older_secret_key(authenticate_user, settings):
    """Test when a new key has been acced after session creation"""
    __, token = authenticate_user

    settings.AUTH_JWT_SECRET_KEYS = 'HS512:new_key,HS512:test_key'

    api_session, __ = APISession.authenticate_token(token)
    assert api_session.user.username == TEST_USERNAME


@pytest.mark.django_db(transaction=True)
def test_authenticate_token_invalid_secret(authenticate_user, settings):
    """Test when the old key has been removed"""
    __, token = authenticate_user

    settings.AUTH_JWT_SECRET_KEYS = 'HS512:new_key'

    with pytest.raises(AuthenticationError):
        APISession.authenticate_token(token)
