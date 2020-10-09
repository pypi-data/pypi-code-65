import threading

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .mysql_config import EasyMySQLConfig
from .mysql_log import EasyMySQLLog


class EasyMysqlManager:
    """
    mysql session manager
    """
    __instance_lock = threading.Lock()
    __engine = None
    __map_base = None
    logger = EasyMySQLLog.logger()
    __engine_config_dic = {}

    @staticmethod
    def init_engine(config_or_yml_path):
        """
        init, require config
        :param config_or_yml_path: yml path or EasyMySQLConfig
        """
        if isinstance(config_or_yml_path, EasyMySQLConfig):
            EasyMysqlManager.__engine_config_dic = config_or_yml_path.__dict__
        elif isinstance(config_or_yml_path, str):
            EasyMysqlManager.__engine_config_dic = EasyMySQLConfig(config_or_yml_path).__dict__
        else:
            raise TypeError('config_or_yml_path: need str or EasyMySQLConfig')
        EasyMysqlManager.logger.info('EasyMysqlManager engine init start')

    @staticmethod
    def __get_engine():
        """
        get mysql engine, singleton
        :return:
        """
        if EasyMysqlManager.__engine is None:
            with EasyMysqlManager.__instance_lock:
                if EasyMysqlManager.__engine is None:
                    url = EasyMysqlManager.__engine_config_dic['url']
                    encoding = EasyMysqlManager.__engine_config_dic['encoding']
                    pool_size = EasyMysqlManager.__engine_config_dic['pool_size']
                    echo = EasyMysqlManager.__engine_config_dic['echo']
                    EasyMysqlManager.__engine = create_engine(url, encoding=encoding,
                                                              pool_size=pool_size,
                                                              echo=echo)
                    EasyMysqlManager.__map_base = declarative_base()
                    EasyMysqlManager.logger.info('EasyMysqlManager engine init success')
        return EasyMysqlManager.__engine

    @property
    def map_base(self):
        """
        get MapBase(super class), mapping class to database table
        :return:
        """
        EasyMysqlManager.__get_engine()
        return EasyMysqlManager.__map_base

    @property
    def session(self):
        """
        get mysql session
        @property: use method as property
        :return:
        """
        EasyMysqlManager.__get_engine()
        db_session = sessionmaker(bind=EasyMysqlManager.__engine)
        return db_session()
