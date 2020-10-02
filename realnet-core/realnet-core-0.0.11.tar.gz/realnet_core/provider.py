from abc import ABC, abstractmethod

class Provider(ABC):

    @abstractmethod
    def get(self, id):
        pass

    @abstractmethod
    def find(self, query, cursor):
        pass


class ItemProvider(Provider):

    def get(self, id):
        pass

    def find(self, query, cursor):
        pass


class TypeProvider(Provider):

    def get(self, id):
        pass

    def find(self, query, cursor):
        pass


class DataProvider(Provider):

    def get(self, id):
        pass

    def find(self, query, cursor):
        pass