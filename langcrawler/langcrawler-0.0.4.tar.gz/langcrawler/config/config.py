# -*- coding: utf-8 -*-


class ConfigException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Config(object):
    hosts = ["gerrit", "github", "gitlab"]
    langs = ["go", "javascript", "php", "python", "rust", "typescript"]

    def __init__(self):
        self._pg_host = "127.0.0.1"
        self._pg_port = 5432
        self._pg_user = "postgres"
        self._pg_pass = "postgres"

        self._redis_host = "127.0.0.1"
        self._redis_port = 6379
        self._redis_pass = "redis"

        self._repo_count = 1
        self._repo_host = []
        self._repo_lang = []

    @property
    def pg_host(self):
        return self._pg_host

    @pg_host.setter
    def pg_host(self, host):
        if not isinstance(host, str) or len(host.strip()) == 0:
            raise ConfigException("host invalid")
        self._pg_host = host

    @property
    def pg_port(self):
        return self._pg_port

    @pg_port.setter
    def pg_port(self, port):
        if not isinstance(port, int) or port <= 0:
            raise ConfigException("port invalid")
        self._pg_port = port

    @property
    def pg_user(self):
        return self._pg_user

    @pg_user.setter
    def pg_user(self, user):
        if not isinstance(user, str) or len(user.strip()) == 0:
            raise ConfigException("user invalid")
        self._pg_user = user

    @property
    def pg_pass(self):
        return self._pg_pass

    @pg_pass.setter
    def pg_pass(self, _pass):
        if not isinstance(_pass, str) or len(_pass.strip()) == 0:
            raise ConfigException("pass invalid")
        self._pg_pass = _pass

    @property
    def redis_host(self):
        return self._redis_host

    @redis_host.setter
    def redis_host(self, host):
        if not isinstance(host, str) or len(host.strip()) == 0:
            raise ConfigException("host invalid")
        self._redis_host = host

    @property
    def redis_port(self):
        return self._redis_port

    @redis_port.setter
    def redis_port(self, port):
        if not isinstance(port, int) or port <= 0:
            raise ConfigException("port invalid")
        self._redis_port = port

    @property
    def redis_pass(self):
        return self._redis_pass

    @redis_pass.setter
    def redis_pass(self, _pass):
        if not isinstance(_pass, str) or len(_pass.strip()) == 0:
            raise ConfigException("pass invalid")
        self._redis_pass = _pass

    @property
    def repo_count(self):
        return self._repo_count

    @repo_count.setter
    def repo_count(self, count):
        if not isinstance(count, int) or count <= 0:
            raise ConfigException("count invalid")
        self._repo_count = count

    @property
    def repo_host(self):
        return self._repo_host

    @repo_host.setter
    def repo_host(self, host):
        if not isinstance(host, list) or len(host) == 0:
            raise ConfigException("host invalid")
        for item in host:
            if item.strip() not in self.hosts:
                raise ConfigException("host invalid: %s" % item)
            self._repo_host.append(item)

    @property
    def repo_lang(self):
        return self._repo_lang

    @repo_lang.setter
    def repo_lang(self, lang):
        if not isinstance(lang, list) or len(lang) == 0:
            raise ConfigException("lang invalid")
        for item in lang:
            if item.strip() not in self.langs:
                raise ConfigException("lang invalid: %s" % item)
            self._repo_lang.append(item)
