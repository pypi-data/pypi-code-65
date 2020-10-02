from abc import ABC, abstractmethod


class Action(ABC):

    @abstractmethod
    def map(self, object, function):
        pass

