import re
from .object import Object

class Param(Object):
    def __init__(self, name, default_value = 0, is_editable = True):
        Object.__init__(self, name)
        self.__default_value = default_value
        if not isinstance(is_editable, bool):
            raise Exception('is_editable is boolean')
        self.__is_editable = is_editable
        self.value = self.__default_value

    def is_editable(self):
        return self.__is_editable

    def set_value(self, value):
        if not self.__is_editable:
            raise Exception('[' + self.get_object_name() + '] is not an editable param')
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self):
        return self.get_object_name() + ' = ' + str(self.get_value())

    def get_string(self):
        return self.get_object_name() + '=' + str(self.get_value())

    __repr__ = __str__
