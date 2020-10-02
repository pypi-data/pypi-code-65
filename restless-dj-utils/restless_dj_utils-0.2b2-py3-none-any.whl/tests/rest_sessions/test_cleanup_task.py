import datetime
import pytest

from django.contrib.auth import get_user_model

from restless_dj_utils.rest_sessions.models import APISession
from restless_dj_utils.rest_sessions.tasks import _cleanup_expired_session_access_database
from restless_dj_utils.tests.conftest import TEST_USERNAME, REMOTE_ADDRESS, USER_AGENT

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_cleanup_expired_session_access_database(create_user):
    """Test cleaning up db backend"""

    user = User.objects.get(username=TEST_USERNAME)
    api_session1 = APISession.objects.create_session(user, REMOTE_ADDRESS, USER_AGENT)[0]
    api_session1.accesses.create()

    api_session2 = APISession.objects.create_session(user, REMOTE_ADDRESS, USER_AGENT)[0]
    api_session2.is_active = False
    api_session2.save(update_fields=['is_active'])

    api_session3 = APISession.objects.create_session(user, REMOTE_ADDRESS, USER_AGENT)[0]
    api_session3.is_active = False
    api_session3.save(update_fields=['is_active'])
    latest = api_session3.accesses.create()

    _cleanup_expired_session_access_database()

    assert api_session1.accesses.count() == 2
    assert api_session2.accesses.count() == 1
    assert api_session3.accesses.count() == 1
    assert api_session3.accesses.get().created == latest.created
