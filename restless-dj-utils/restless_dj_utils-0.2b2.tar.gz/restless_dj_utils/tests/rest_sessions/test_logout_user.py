import pytest

from restless_dj_utils.rest_sessions.models import APISession


@pytest.mark.django_db(transaction=True)
def test_logout_user(authenticate_user):
    """Test user logout"""
    api_session, token = authenticate_user

    assert api_session.is_active is True

    APISession.logout_user(token)

    api_session.refresh_from_db()
    assert api_session.is_active is False
