from .redis_config import EasyRedisConfig
from .redis_conn import EasyRedis
from .redis_log import EasyRedisLog


class EasyRedisConsumer:
    __config_dic = {}
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
        self.redis_conn = EasyRedis(config_or_yml_path).redis_conn
        self.consumer = self.redis_conn.pubsub()
        self.consumer.subscribe(self.__config_dic['channel_subscribe'])
        self.logger.info('consumer started[channel: {}]'.format(
            self.__config_dic['channel_subscribe']))

    def __iter__(self):
        return self.consumer.listen().__iter__()

    def __next__(self):
        return self.consumer.listen().__next__()

    def subscribe(self, fn):
        """
        subscribe with callback fn(record), blocked
        def task(record):
            ...
        redis_consumer.subscribe(task)
        :param fn: method, require one parameter
        """
        for record in self:
            self.logger.info(
                'received type: {}, channel: {}, msg: {}'.format(record['type'], record['channel'], record['data']))
            fn(record)
