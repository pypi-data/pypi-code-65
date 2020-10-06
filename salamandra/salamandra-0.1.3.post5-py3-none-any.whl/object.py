class Object(object):
    def __init__(self, name):
        self.__name = name

    def get_object_name(self):
        return self.__name

    def set_object_name(self, name):
        self.__name = name

    def __str__(self):
        return self.__name

