import json

import redis
from django.conf import settings

from .exceptions import RGRedisException
from .. import rg_logger


class RedisCache:
    __connection = None

    def __init__(self, redis_settings_key: str = "DEFAULT"):
        self.redis_settings_key = redis_settings_key

    def __get_connection(self):
        if not self.__connection:
            redis_settings = self.__get_redis_settings(self.redis_settings_key)
            redis_connection = self.__init_redis_connection_with_settings(redis_settings, self.redis_settings_key)
            self.__connection = redis_connection
        else:
            pass

        # rg_logger.info("settingKey: " + self.redis_settings_key)
        return self.__connection

    @classmethod
    def __init_redis_connection_with_settings(cls, redis_settings: dict, redis_setting_key: str):
        try:
            if not redis_settings and ("HOST" not in redis_settings or "PORT" not in redis_settings not in "DB" in redis_settings and "PASSWORD" not in redis_settings):
                raise RGRedisException("Redis setting not proper defined in settings.py, current settings=" + json.dumps(redis_settings))

            connection = redis.Redis(
                host=redis_settings["HOST"],
                port=redis_settings["PORT"],
                db=redis_settings["DB"],
                password=redis_settings["PASSWORD"],
                socket_connect_timeout=redis_settings["TIMEOUT"],
                socket_timeout=redis_settings["TIMEOUT"],
                decode_responses=True)

            if connection:
                rg_logger.info_important("Host:{}, Port:{}, DB:{}, SettingKey: {}".format(redis_settings["HOST"], redis_settings["PORT"], redis_settings["DB"], redis_setting_key))

            return connection
        except Exception as e:
            raise RGRedisException("Error in Redis Connection, method=RedisCache->__init_redis_connection_with_settings")

    @staticmethod
    def __get_redis_settings(redis_setting_key: str) -> dict:
        redis_settings_dict = getattr(settings, "REDIS_SETTINGS", None)

        if redis_settings_dict and redis_setting_key in redis_settings_dict:
            return redis_settings_dict[redis_setting_key]
        else:
            raise RGRedisException("Redis setting not proper defined in settings.py, Not found REDIS_SETTINGS or no key=" + redis_setting_key)

    def put_value_in_hash_set(self, redis_key: str, _hash_key: str, _hash_value: str):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                redis_connection.hset(redis_key, _hash_key, str(_hash_value))
            except Exception as e:
                rg_logger.exception(e, "RedisCache->put_value_in_hash_set()->>")
                raise RGRedisException("RedisCache->put_value_in_hash_set()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + redis_key + ", method=put_value_in_hash_set")

    def get_value_from_hash_set(self, redis_key: str, _key):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.hget(redis_key, _key)
            except Exception as e:
                raise RGRedisException("RedisCache->get_value_from_hash_set()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + redis_key + ", method=get_value_from_hash_set")

    def get_all_values_from_hash_set(self, _redis_key: str):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.hgetall(_redis_key)
            except Exception as e:
                raise RGRedisException("RedisCache->get_all_values_from_hash_set()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + _redis_key + ", method=get_all_values_from_hash_set")

    def remove_value_from_hash_set(self, _redis_key: str, _hash_key: str):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.hdel(_redis_key, _hash_key)
            except Exception as e:
                raise RGRedisException("RedisCache->remove_value_from_hash_set()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + _redis_key + ", method=remove_value_from_hash_set")

    def delete_key_from_cache(self, _redis_key: str):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.delete(_redis_key)
            except Exception as e:
                raise RGRedisException("RedisCache->delete_key_from_cache()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + _redis_key + ", method=delete_key_from_cache")

    def put_string_value(self, _redis_key: str, _value: str):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.set(_redis_key, _value)
            except Exception as e:
                raise RGRedisException("RedisCache->put_string_value()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + _redis_key + ", method=put_string_value")

    def get_string_value(self, _redis_key):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.get(_redis_key)
            except Exception as e:
                raise RGRedisException("RedisCache->get_string_value()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + _redis_key + ", method=get_string_value")

    def incr_value(self, _redis_key):
        redis_connection = self.__get_connection()

        if redis_connection:
            try:
                return redis_connection.incr(_redis_key)
            except Exception as e:
                raise RGRedisException("RedisCache->incr_value()->>" + rg_logger.get_exception_msg(e))
        else:
            raise RGRedisException("Redis Connection Error for key=" + _redis_key + ", method=incr_value")
