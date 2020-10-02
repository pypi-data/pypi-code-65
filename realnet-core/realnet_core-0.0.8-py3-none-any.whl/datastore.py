from abc import ABC, abstractmethod


class DataStore(ABC):

    @abstractmethod
    def create_data(self, data, attributes=None):
        pass

    @abstractmethod
    def put_data(self, data):
        pass

    @abstractmethod
    def get_data(self, id):
        pass

    @abstractmethod
    def delete_data(self, id):
        pass

