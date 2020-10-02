import pytest

from django.contrib.auth import get_user_model


from restless_dj_utils.exceptions import AuthenticationError
from restless_dj_utils.rest_sessions.models import APISession
from restless_dj_utils.tests.conftest import TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_authenticate_user(create_user):
    """Test user authentication"""
    api_session, token = APISession.authenticate_user(
        TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT)

    assert api_session.user.username == TEST_USERNAME
    assert api_session.is_active is True
    assert api_session.remote_address == REMOTE_ADDRESS
    assert api_session.user_agent == {
        'device': {
            'brand': 'Huawei',
            'family': 'Huawei Nexus 6P',
            'model': 'Nexus 6P'
        },
        'os': {
            'family': 'Android',
            'major': '6',
            'minor': '0',
            'patch': '1',
            'patch_minor': None
        },
        'string': USER_AGENT,
        'user_agent': {
            'family': 'Chrome Mobile',
            'major': '47',
            'minor': '0',
            'patch': '2526'
        }
    }

    token_data = APISession.objects.decode_token(token)
    assert token_data['user_id'] == api_session.user.id
    assert token_data['session_id'] == api_session.id
    assert api_session.get_token_data() == token_data


@pytest.mark.django_db(transaction=True)
def test_authenticate_user_invalid_password(create_user):
    """Test with invalid password"""
    with pytest.raises(AuthenticationError):
        APISession.authenticate_user(TEST_USERNAME, 'invalid', REMOTE_ADDRESS, USER_AGENT)


@pytest.mark.django_db(transaction=True)
def test_authenticate_user_inactive_user(create_user):
    """Test when user is deactivated"""
    user = User.objects.get(username=TEST_USERNAME)
    user.is_active = False
    user.save(update_fields=['is_active'])

    with pytest.raises(AuthenticationError):
        APISession.authenticate_user(TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT)


@pytest.mark.django_db(transaction=True)
def test_authenticate_user_no_user():
    """Test when no user exists"""
    with pytest.raises(AuthenticationError):
        APISession.authenticate_user(TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT)
