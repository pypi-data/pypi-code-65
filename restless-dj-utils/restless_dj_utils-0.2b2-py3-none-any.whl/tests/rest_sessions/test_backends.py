import datetime
import pytest

from unittest import mock
from django.utils import timezone
from django.core.cache import cache

from restless_dj_utils.exceptions import SessionExpiredError
from restless_dj_utils.rest_sessions.backends import (
    DBSessionAccessBackend, CacheSessionAccessBackend, CachedDBSessionAccessBackend)
from restless_dj_utils.rest_sessions.conf import INACTIVITY_TIMEOUT


# DBSessionAccessBackend

@pytest.mark.django_db(transaction=True)
def test_db_backend_log_session_access(api_session):
    """Test logging user access"""
    backend = DBSessionAccessBackend()

    assert api_session.accesses.count() == 0

    backend.log_session_access(api_session, INACTIVITY_TIMEOUT, True)

    assert api_session.accesses.count() == 1


@pytest.mark.django_db(transaction=True)
def test_db_backend_log_session_access_not_recently_used(api_session):
    """Test when user has not accessed"""
    backend = DBSessionAccessBackend()
    now = timezone.now()

    last_access = timezone.now() - datetime.timedelta(seconds=INACTIVITY_TIMEOUT + 1)
    api_session.accesses.create()
    api_session.accesses.update(created=last_access)

    with mock.patch('django.utils.timezone.now', return_value=now):
        with pytest.raises(SessionExpiredError):
            backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    assert api_session.accesses.count() == 1


@pytest.mark.django_db(transaction=True)
def test_db_backend_log_session_access_recently_used(api_session):
    """Test when user has accessed"""
    backend = DBSessionAccessBackend()
    now = timezone.now()

    last_access = timezone.now() - datetime.timedelta(seconds=INACTIVITY_TIMEOUT)
    api_session.accesses.create()
    api_session.accesses.update(created=last_access)

    with mock.patch('django.utils.timezone.now', return_value=now):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    assert api_session.accesses.count() == 2


# CacheSessionAccessBackend

@pytest.mark.django_db(transaction=True)
def test_cache_backend_log_session_access(api_session):
    """Test logging user access"""
    backend = CacheSessionAccessBackend()

    backend.log_session_access(api_session, INACTIVITY_TIMEOUT, True)

    cache_key = backend._get_key(api_session)
    assert bool(cache.get(cache_key)) is True


@pytest.mark.django_db(transaction=True)
def test_cache_backend_log_session_access_not_recently_used(api_session):
    """Test when user has not accessed"""
    backend = CacheSessionAccessBackend()

    with pytest.raises(SessionExpiredError):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    cache_key = backend._get_key(api_session)
    assert cache.get(cache_key) is None


@pytest.mark.django_db(transaction=True)
def test_cache_backend_log_session_access_recently_used(api_session):
    """Test when user has accessed"""
    backend = CacheSessionAccessBackend()

    cache_key = backend._get_key(api_session)
    cache.set(cache_key, True)

    now = timezone.now()
    with mock.patch('django.utils.timezone.now', return_value=now):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    assert cache.get(cache_key) == now


# CachedDBSessionAccessBackend

@pytest.mark.django_db(transaction=True)
def test_cached_db_backend_log_session_access(api_session):
    """Test logging user access"""
    backend = CachedDBSessionAccessBackend()
    cache_key = backend._get_key(api_session)
    now = timezone.now()

    assert api_session.accesses.count() == 0

    with mock.patch('django.utils.timezone.now', return_value=now):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, True)

    stored_cache = cache.get(cache_key)
    assert stored_cache['created'] == now
    assert stored_cache['last_db_save'] == now
    assert api_session.accesses.count() == 1


@pytest.mark.django_db(transaction=True)
def test_cached_db_backend_log_session_access_no_db(api_session):
    """Test logging user access when recently saved to db"""
    backend = CachedDBSessionAccessBackend()
    cache_key = backend._get_key(api_session)

    now = timezone.now()
    last_db_save = now - datetime.timedelta(seconds=59)

    cache.set(cache_key, {
        'created': last_db_save,
        'last_db_save': last_db_save
    })

    with mock.patch('django.utils.timezone.now', return_value=now):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    stored_cache = cache.get(cache_key)
    assert stored_cache['created'] == now
    assert stored_cache['last_db_save'] == last_db_save
    assert api_session.accesses.count() == 0


@pytest.mark.django_db(transaction=True)
def test_cached_db_backend_log_session_access_with_db(api_session):
    """Test logging user access when not recently saved to db"""
    backend = CachedDBSessionAccessBackend()
    cache_key = backend._get_key(api_session)

    now = timezone.now()
    last_db_save = now - datetime.timedelta(seconds=60)

    cache.set(cache_key, {
        'created': last_db_save,
        'last_db_save': last_db_save
    })

    with mock.patch('django.utils.timezone.now', return_value=now):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    stored_cache = cache.get(cache_key)
    assert stored_cache['created'] == now
    assert stored_cache['last_db_save'] == now
    assert api_session.accesses.count() == 1


@pytest.mark.django_db(transaction=True)
def test_cached_db_backend_log_session_access_not_recently_used(api_session):
    """Test when user has not accessed"""
    backend = CachedDBSessionAccessBackend()

    with pytest.raises(SessionExpiredError):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    cache_key = backend._get_key(api_session)
    assert cache.get(cache_key) is None
    assert api_session.accesses.count() == 0


@pytest.mark.django_db(transaction=True)
def test_cached_db_backend_log_session_access_recently_used_no_cache(api_session):
    """Test when user has accessed but cache has expired"""
    backend = CachedDBSessionAccessBackend()
    now = timezone.now()

    last_access = now - datetime.timedelta(seconds=INACTIVITY_TIMEOUT - 1)
    api_session.accesses.create()
    api_session.accesses.update(created=last_access)

    with mock.patch('django.utils.timezone.now', return_value=now):
        backend.log_session_access(api_session, INACTIVITY_TIMEOUT, False)

    cache_key = backend._get_key(api_session)
    stored_cache = cache.get(cache_key)
    assert stored_cache['created'] == now
    assert stored_cache['last_db_save'] == now
    assert api_session.accesses.count() == 2
