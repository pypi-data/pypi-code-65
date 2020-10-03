from abc import *

class AbstractModel:
    @abstractmethod
    def get_table_name (self):
        pass

    @classmethod
    def get_columns (self):
        raise NotImplementedError ('return column list like [name, ...]')

    @classmethod
    def validate (self, data, create = False):
        raise NotImplementedError

    @classmethod
    def get_pk (self):
        raise NotImplementedError ('return pk column name like id')

    @classmethod
    def get_fks (self):
        raise NotImplementedError ('return fks like {fk_alias: (fk_column, fk_model)}')
