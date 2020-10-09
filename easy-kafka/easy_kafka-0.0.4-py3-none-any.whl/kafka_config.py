import os

import yaml

from .kafka_log import EasyKafkaLog


class EasyKafkaConfig:
    bootstrap_servers = '127.0.0.1:9092'
    group_id = 'demo'
    topic_subscribe = 'demo_topic'
    topic_produce = 'demo_topic'
    logger = EasyKafkaLog.logger()

    def __init__(self, yml_path):
        """
        yml config file
        :param yml_path:
        """
        if not os.path.exists(yml_path):
            raise FileNotFoundError('yml config not found')
        # parse
        with open(yml_path, encoding='UTF-8') as f:
            data = f.read()
            conf = yaml.load(data, Loader=yaml.FullLoader)
            self.bootstrap_servers = conf['kafka'].get('bootstrap_servers')
            self.group_id = conf['kafka'].get('group_id')
            self.topic_subscribe = conf['kafka'].get('topic_subscribe')
            self.topic_produce = conf['kafka'].get('topic_produce')
            self.logger.info('KafkaConfig: yml parse done')
