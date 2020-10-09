from pymongo import MongoClient

from .mongo_config import EasyMongoConfig
from .mongo_log import EasyMongoLog


class EasyMongo():
    logger = EasyMongoLog.logger()

    def __init__(self, config_or_yml_path):
        """
        init, require config
        :param config_or_yml_path: yml path or EasyMongoConfig
        """
        if isinstance(config_or_yml_path, EasyMongoConfig):
            self.__config_dic = config_or_yml_path.__dict__
        elif isinstance(config_or_yml_path, str):
            self.__config_dic = EasyMongoConfig(config_or_yml_path).__dict__
        else:
            raise TypeError('config_or_yml_path: need str or EasyMongoConfig')
        self.connect = MongoClient(host=self.__config_dic['host'], port=self.__config_dic['port'])
        self.db = self.connect[self.__config_dic['name']]
        self.db.authenticate(self.__config_dic['name'], self.__config_dic['password'])
        self.logger.info('mongo connected: %s:%d/%s' % (
            self.__config_dic['host'], self.__config_dic['port'], self.__config_dic['name']))

    def get_db(self):
        return self.db

    def get_collection(self, collection: str):
        return self.db[collection]
