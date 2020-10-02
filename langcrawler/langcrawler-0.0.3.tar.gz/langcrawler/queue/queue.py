# -*- coding: utf-8 -*-

import redis


class QueueException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Queue(object):
    def __init__(self, config=None):
        if config is None:
            raise QueueException("config invalid")

        self._config = config
        self._redis = None

    def connect(self, db=0):
        try:
            self._redis = redis.Redis(
                host=self._config.redis_host,
                port=self._config.redis_port,
                db=db,
                password=self._config.redis_pass,
            )
        except redis.exceptions.ResponseError as e:
            raise QueueException("failed to connect: %s" % str(e))

    def disconnect(self):
        def helper(data):
            try:
                self._redis.client_kill(data)
            except redis.exceptions.ResponseError as e:
                raise QueueException("failed to kill: %s" % str(e))

        for item in self._redis.client_list():
            helper(item["addr"])

    def delete(self, name):
        try:
            keys = self._redis.hkeys(name)
            for item in keys:
                self._redis.hdel(name, item)
        except redis.exceptions.DataError as e:
            raise QueueException("failed to hdel: %s" % str(e))

    def get(self, name):
        try:
            return self._redis.hgetall(name)
        except redis.exceptions.DataError as e:
            raise QueueException("failed to hget: %s" % str(e))

    def set(self, name, key=None, value=None, mapping=None):
        try:
            self._redis.hset(name=name, key=key, value=value, mapping=mapping)
        except redis.exceptions.DataError as e:
            raise QueueException("failed to hset: %s" % str(e))
