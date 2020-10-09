import threading

from kafka import KafkaConsumer

from .kafka_config import EasyKafkaConfig
from .kafka_log import EasyKafkaLog


class EasyKafkaConsumer:
    __config_dic = {}
    logger = EasyKafkaLog.logger()

    def __init__(self, config_or_yml_path):
        """
        init, require config
        :param config_or_yml_path: yml path or EasyKafkaConfig
        """
        if isinstance(config_or_yml_path, EasyKafkaConfig):
            self.__config_dic = config_or_yml_path.__dict__
        elif isinstance(config_or_yml_path, str):
            self.__config_dic = EasyKafkaConfig(config_or_yml_path).__dict__
        else:
            raise TypeError('config_or_yml_path: need str or EasyKafkaConfig')
        self.consumer = KafkaConsumer(bootstrap_servers=self.__config_dic['bootstrap_servers'],
                                      group_id=self.__config_dic['group_id'])
        self.consumer.subscribe(self.__config_dic['topic_subscribe'])
        self.logger.info('consumer started[topic: {}, group_id: {}]'.format(
            self.__config_dic['topic_subscribe'], self.__config_dic['group_id']))

    def __iter__(self):
        return self.consumer

    def __next__(self):
        return self.consumer.__next__()

    def subscribe(self, fn, thread=False):
        """
        subscribe with callback fn(record), blocked default(thread=False)
        def task(record):
            ...
        kafka_consumer.subscribe(task)
        :param fn: method, require one parameter
        :param thread: new thread to handle if thread=True
        """
        self.logger.info('consumer task started, mode={}'.format('async' if thread else 'blocked'))
        for record in self:
            self.logger.info('received topic: {}, msg: {}'.format(record.topic, record.value))
            if thread:
                threading.Thread(target=fn, args=(record,)).start()
            else:
                fn(record)
