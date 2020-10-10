SECRET_KEY = "django_tests_secret_key"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://127.0.0.1:7000",
        "LOCATION": [{"host": "127.0.0.1", "port": 7000}],
        "OPTIONS": {
            "CLIENT_CLASS": "hypersRedisCluster.client.RedisClusterClient",
            # "REDIS_CLIENT_KWARGS": {"ssl_cert_reqs": None, "ssl":True},
        },
    }
}

INSTALLED_APPS = ("django.contrib.sessions",)
