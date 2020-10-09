import os

import yaml

from .mysql_log import EasyMySQLLog


class EasyMySQLConfig:
    url = 'mysql://root:password@127.0.0.1:3306/db'  # mysql server
    encoding = 'utf-8'
    pool = 5  # pool size
    echo = False  # echo sql while executing
    logger = EasyMySQLLog.logger()

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
            self.url = conf['mysql'].get('url')
            self.encoding = conf['mysql'].get('encoding')
            self.pool_size = conf['mysql'].get('pool_size')
            self.echo = conf['mysql'].get('echo')
            self.logger.info('EasyMySQLLog: yml parse done')
