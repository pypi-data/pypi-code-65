import datetime

from django.utils import timezone
from django.core.cache import cache

from restless_dj_utils.exceptions import SessionExpiredError


class DBSessionAccessBackend:
    """
    Last access is stored in a database table, a new entry is inserted on each request
    """

    def get_last_access(self, api_session):
        return api_session.accesses.latest().created

    def log_session_access(self, api_session, inactivity_timeout, is_new):
        """"""

        if not is_new:
            cutoff = timezone.now() - datetime.timedelta(seconds=inactivity_timeout)
            if api_session.accesses.filter(created__gte=cutoff).count() == 0:
                raise SessionExpiredError()

        api_session.accesses.create()


class CacheSessionAccessBackend:
    """
    Last access is stored in the cache
    """

    def _get_key(self, api_session):
        return f'session_{api_session.id}'

    def get_last_access(self, api_session):
        cache_key = self._get_key(api_session)
        return cache.get(cache_key)

    def log_session_access(self, api_session, inactivity_timeout, is_new):
        """"""

        if not is_new:
            result = self.get_last_access(api_session)
            if result is None:
                raise SessionExpiredError()

        cache_key = self._get_key(api_session)
        cache.set(cache_key, timezone.now(), timeout=inactivity_timeout)


class CachedDBSessionAccessBackend:
    """
    Last access is stored in cache and inserted into the database once every 60 seconds
    """

    def _get_key(self, api_session):
        return f'session_{api_session.id}'

    def get_last_access(self, api_session):
        cache_key = self._get_key(api_session)
        result = cache.get(cache_key)
        if result:
            return result['created']

        return api_session.accesses.latest().created

    def log_session_access(self, api_session, inactivity_timeout, is_new):
        """"""

        last_db_save = None

        if not is_new:
            cache_key = self._get_key(api_session)
            result = cache.get(cache_key)
            if result is None:
                cutoff = timezone.now() - datetime.timedelta(seconds=inactivity_timeout)
                if api_session.accesses.filter(created__gte=cutoff).count() == 0:
                    raise SessionExpiredError()
            else:
                last_db_save = result['last_db_save']

        # Log session access
        custoff = timezone.now() - datetime.timedelta(seconds=60)
        if not last_db_save or last_db_save <= custoff:
            access = api_session.accesses.create()
            last_db_save = access.created

        cache_key = self._get_key(api_session)
        data = {
            'created': timezone.now(),
            'last_db_save': last_db_save
        }
        cache.set(cache_key, data, timeout=inactivity_timeout)
