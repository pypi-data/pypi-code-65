import os

import yaml
from .mongo_log import EasyMongoLog


class EasyMongoConfig:
    host = '127.0.0.1'
    port = 27017
    name = 'name'
    password = 'password'
    logger = EasyMongoLog.logger()

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
            self.host = conf['mongo'].get('host')
            self.port = conf['mongo'].get('port')
            self.name = conf['mongo'].get('name')
            self.password = conf['mongo'].get('password')
            self.logger.info('EasyMongoConfig: yml parse done')


if __name__ == "__main__":
    config = EasyMongoConfig('../conf/conf.yml')
    print(config.__dict__)
