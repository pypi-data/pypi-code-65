from typing import Any, Optional

try:
    # Try importing Django app settings to find out whether we are running inside Django
    from django.core.exceptions import ImproperlyConfigured
    from ..django import settings as django_settings
except (ImportError, ImproperlyConfigured):
    USING_DJANGO = False
else:
    from django.core.cache import caches as django_caches

    USING_DJANGO = True
finally:
    try:
        del ImproperlyConfigured
    except NameError:
        # We never got it
        pass  # noqa

try:
    # Try importings ucache's most simple backend
    from ucache import SqliteCache as UCSqliteCache
except ImportError:
    USING_UCACHE = False
else:
    USING_UCACHE = True

if USING_DJANGO:
    # Get Django cache designated by BBB_CACHE_NAME setting, or "default"
    cache = django_caches[django_settings.CACHE_NAME]
elif USING_UCACHE:
    from getpass import getuser
    from pathlib import Path
    from tempfile import gettempdir

    # Create temporary directory to hold cache data
    tempdir = Path(gettempdir(), f"python-bigbluebutton2-{getuser()}")
    tempdir.mkdir(mode=0o700, parents=True, exist_ok=True)

    cache = UCSqliteCache(str(tempdir.joinpath("cache.sqlite")))
else:
    # No caching backend found, make caching a no-op
    class DummyCache:
        def _dummy(self, *args, **lwargs) -> None:
            return

        get = _dummy
        get_many = _dummy
        set = _dummy
        set_many = _dummy
        delete = _dummy
        delete_many = _dummy
        flush = _dummy
        clean_expired = _dummy

        __getitem__ = get
        __setitem__ = set
        __delitem__ = delete

    cache = DummyCache()
