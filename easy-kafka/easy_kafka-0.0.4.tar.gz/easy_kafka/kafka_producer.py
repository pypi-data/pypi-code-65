import json

from kafka import KafkaProducer

from .kafka_config import EasyKafkaConfig
from .kafka_log import EasyKafkaLog


class EasyKafkaProducer:
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
        self.producer = KafkaProducer(bootstrap_servers=self.__config_dic['bootstrap_servers'],
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = self.__config_dic['topic_produce']
        self.logger.info('producer started[topic: %s]' % self.topic)

    def produce_msg(self, msg):
        """
        produce msg with default topic
        :param msg:json or dic
        :return:
        """
        self.produce_msg_topic(self.topic, msg)

    def produce_msg_topic(self, topic: str, msg):
        """
        produce msg with topic
        :param topic:
        :param msg:json or dic
        :return:
        """
        self.producer.send(topic, msg)
        self.producer.flush()
