from .easy_manager import EasyMysqlManager


class EasyMySQLDAOBase:
    """
    used to mapping database table, after init
    Database Access Object, to operate Database Table
    usage:

    """

    def __init__(self, map_class):
        """
        init
        :param map_class: subclass
        """
        self.map_class = map_class
        self.mysqlManager = EasyMysqlManager()
        self.map_base = self.mysqlManager.map_base
        self.session = self.mysqlManager.session
        print('base init')

    def find_all(self, *where):
        """
        find all with condition, default 'and_'
            EasyMySQLUtil.find_all(map_class,and_(map_class.name!='name',map_class.age>5))
            EasyMySQLUtil.find_all(map_class,or_(map_class.name!='name',map_class.age>5))
        :param where: for example map_class.name!='name'
        :return:
        """
        obj_list = self.session.query(self.map_class).filter(*where).all()
        return obj_list

    def find_one(self, *where):
        """
        find one with condition, default 'and_'
            EasyMySQLUtil.find_all(map_class,and_(map_class.name!='name',map_class.age>5))
            EasyMySQLUtil.find_all(map_class,or_(map_class.name!='name',map_class.age>5))
        :param where: for example map_class.name!='name'
        :return:
        """
        obj = self.session.query(self.map_class).filter(*where).one()
        return obj

    def update(self, *where, **update):
        """
        find all with condition, default 'and_'
            EasyMySQLUtil.find_all(map_class,and_(map_class.name!='name',map_class.age>5),name='name')
            EasyMySQLUtil.find_all(map_class,or_(map_class.name!='name',map_class.age>5),name='name')
        :param where: for example map_class.name!='name'
        :param update: for example name='name'
        :return:
        """
        result = self.session.query(self.map_class).filter(*where).update(update)
        self.session.commit()
        return result

    def add(self, map_class_obj):
        """
        add one object
            EasyMySQLUtil.add(map_class)
        :param map_class_obj: obj
        :return:
        """
        self.session.add(map_class_obj)
        self.session.commit()
        return map_class_obj

    def add_all(self, map_class_obj_list: list):
        """
        add object list
            EasyMySQLUtil.add_all(map_class_obj_list)
        :param map_class_obj_list: entity
        :return:
        """
        self.session.add_all(map_class_obj_list)
        self.session.commit()
        return map_class_obj_list

    def delete(self, *where):
        """
        delete from where
        :param where: condition
        :return:
        """
        result = self.session.query(self.map_class).filter(*where).delete()
        self.session.commit()
        return result
