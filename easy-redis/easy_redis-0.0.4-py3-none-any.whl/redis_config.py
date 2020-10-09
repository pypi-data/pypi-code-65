import os

import yaml

from .redis_log import EasyRedisLog


class EasyRedisConfig:
    server = '127.0.0.1'
    port = 6379
    channel_subscribe = ['demo_channel']
    channel_produce = 'demo_channel'
    logger = EasyRedisLog.logger()

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
            self.server = conf['redis'].get('server')
            self.port = conf['redis'].get('port')
            self.channel_subscribe = conf['redis'].get('channel_subscribe')
            self.channel_produce = conf['redis'].get('channel_produce')
            self.logger.info('EasyRedisConfig: yml parse done')
