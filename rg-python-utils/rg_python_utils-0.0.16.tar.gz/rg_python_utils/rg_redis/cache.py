from rg_python_utils.rg_redis.redis_cache import RedisCache


class Cache:
    def __init__(self, redis_key: str):
        self._redis_key = redis_key
        self._cache_connection = None
        self._local_cache_version = None
        super().__init__()

    def _get_cache(self) -> RedisCache:
        if not self._cache_connection:
            self._cache_connection = RedisCache(self._redis_key)

        return self._cache_connection

    def get_redis_cache_version(self):
        return self._get_cache().get_string_value(self._redis_key)

    def is_redis_cache_version_changed(self) -> bool:
        if self.get_redis_cache_version():
            return not self._local_cache_version or self.get_redis_cache_version() != self._local_cache_version
        else:
            pass

    def update_local_cache_version_with_redis_version(self):
        self._local_cache_version = self.get_redis_cache_version()

    def increase_redis_version(self):
        self._get_cache().incr_value(self._redis_key)
