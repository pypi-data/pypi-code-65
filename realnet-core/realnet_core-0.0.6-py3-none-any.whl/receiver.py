from abc import ABC, abstractmethod

class Receiver(ABC):

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def put(self, object):
        pass


class ItemReceiver(Receiver):

    def create(self, *args, **kwargs):
        pass

    def put(self, object):
        pass


class TypeReceiver(Receiver):

    def create(self, *args, **kwargs):
        pass

    def put(self, object):
        pass


class DataReceiver(Receiver):

    def create(self, *args, **kwargs):
        pass

    def put(self, object):
        pass