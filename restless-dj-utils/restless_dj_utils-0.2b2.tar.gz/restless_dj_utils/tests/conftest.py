import pytest

from django.contrib.auth import get_user_model
from django.core.cache import cache

from restless_dj_utils.rest_sessions.models import APISession

User = get_user_model()


TEST_USERNAME = "test-user@example.com"
TEST_PASSWORD = "somepass&92j3^"
REMOTE_ADDRESS = '192.168.1.1'
USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 ' \
             'Mobile Safari/537.36'


@pytest.fixture(scope="function")
def create_user(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = User.objects.create(username=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.save(update_fields=["password"])


@pytest.fixture(scope="function")
def api_session(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = User.objects.create(username=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.save(update_fields=["password"])

        api_session = APISession.objects.create_session(
            user, REMOTE_ADDRESS, USER_AGENT)[0]
        api_session.accesses.all().delete()
        cache.delete(f'session_{api_session.id}')
        return api_session


@pytest.fixture(scope="function")
def authenticate_user(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = User.objects.create(username=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.save(update_fields=["password"])
        api_session, token = APISession.authenticate_user(
            TEST_USERNAME, TEST_PASSWORD, REMOTE_ADDRESS, USER_AGENT)
        return api_session, token
