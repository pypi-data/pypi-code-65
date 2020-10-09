import functools

from .easy_manager import EasyMysqlManager


class EasyMySQLUtil:
    """
    simple CURD operation
    """
    mysqlManager = None
    map_base = None
    session = None

    @staticmethod
    def init(config_or_yml_path):
        """
        require init -> forward to mysql manager init
        :param config_or_yml_path: yml path or EasyMySQLConfig
        :return:
        """
        EasyMysqlManager.init_engine(config_or_yml_path)
        EasyMySQLUtil.mysqlManager = EasyMysqlManager()
        EasyMySQLUtil.map_base = EasyMySQLUtil.mysqlManager.map_base
        EasyMySQLUtil.session = EasyMySQLUtil.mysqlManager.session

    @staticmethod
    def find_all(map_class, *where):
        """
        find all with condition, default 'and_'
            EasyMySQLUtil.find_all(map_class,and_(map_class.name!='name',map_class.age>5))
            EasyMySQLUtil.find_all(map_class,or_(map_class.name!='name',map_class.age>5))
        :param map_class: entity
        :param where: for example map_class.name!='name'
        :return:
        """
        obj_list = EasyMySQLUtil.session.query(map_class).filter(*where).all()
        return obj_list

    @staticmethod
    def find_one(map_class, *where):
        """
        find one with condition, default 'and_'
            EasyMySQLUtil.find_all(map_class,and_(map_class.name!='name',map_class.age>5))
            EasyMySQLUtil.find_all(map_class,or_(map_class.name!='name',map_class.age>5))
        :param map_class: entity
        :param where: for example map_class.name!='name'
        :return:
        """
        obj = EasyMySQLUtil.session.query(map_class).filter(*where).one()
        return obj

    @staticmethod
    def update(map_class, *where, **update):
        """
        find all with condition, default 'and_'
            EasyMySQLUtil.find_all(map_class,and_(map_class.name!='name',map_class.age>5),name='name')
            EasyMySQLUtil.find_all(map_class,or_(map_class.name!='name',map_class.age>5),name='name')
        :param map_class: entity
        :param where: for example map_class.name!='name'
        :param update: for example name='name'
        :return:
        """
        result = EasyMySQLUtil.session.query(map_class).filter(*where).update(update)
        EasyMySQLUtil.session.commit()
        return result

    @staticmethod
    def add(map_class_obj):
        """
        add one object
            EasyMySQLUtil.add(map_class)
        :param map_class_obj: obj
        :return:
        """
        EasyMySQLUtil.session.add(map_class_obj)
        EasyMySQLUtil.session.commit()
        return map_class_obj

    @staticmethod
    def add_all(map_class_obj_list: list):
        """
        add object list
            EasyMySQLUtil.add_all(map_class_obj_list)
        :param map_class_obj_list: entity
        :return:
        """
        EasyMySQLUtil.session.add_all(map_class_obj_list)
        EasyMySQLUtil.session.commit()
        return map_class_obj_list

    @staticmethod
    def delete(map_class, *where):
        """
        delete from where
        :param map_class:
        :param where: condition
        :return:
        """
        result = EasyMySQLUtil.session.query(map_class).filter(*where).delete()
        EasyMySQLUtil.session.commit()
        return result


def mysql_session(method):
    """
    annotation example:
        @mysql_session
        def query_all(map_class, session):
            obj_list = session.query(cls).all()
            return obj_list
    :param method:
    :return:
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        sess = EasyMySQLUtil.session
        kwargs['session'] = sess
        return method(*args, **kwargs)

    return wrapper
