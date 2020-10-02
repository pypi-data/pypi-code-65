from abc import ABC, abstractmethod


class Stream(ABC):

    @abstractmethod
    def something(self):
        pass

