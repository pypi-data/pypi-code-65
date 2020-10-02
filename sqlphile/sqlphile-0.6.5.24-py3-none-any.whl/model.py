from abc import *

class AbstractModel:
    @abstractmethod
    def get_table_name (self):
        pass

    @abstractmethod
    def validate (self, data, create = False):
        pass
