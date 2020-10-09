import redis

from .redis_config import EasyRedisConfig
from .redis_log import EasyRedisLog


class EasyRedis:
    redis_conn = None
    logger = EasyRedisLog.logger()

    def __init__(self, config_or_yml_path):
        """
        init, require config
        :param config_or_yml_path: yml path or EasyRedisConfig
        """
        if isinstance(config_or_yml_path, EasyRedisConfig):
            self.__config_dic = config_or_yml_path.__dict__
        elif isinstance(config_or_yml_path, str):
            self.__config_dic = EasyRedisConfig(config_or_yml_path).__dict__
        else:
            raise TypeError('config_or_yml_path: need str or EasyRedisConfig')
        self.redis_conn = redis.Redis(host=self.__config_dic['server'], port=self.__config_dic['port'],
                                      decode_responses=True)
        self.logger.info('redis conn started[server: {}, port: {}]'.format(
            self.__config_dic['server'], self.__config_dic['port']))
