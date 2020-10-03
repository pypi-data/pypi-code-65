from abc import ABC, abstractmethod

from tweepy.models import Status


class BaseStorageBackend(ABC):
    @abstractmethod
    def persist_status(self, status: Status) -> None:
        """
        This method should store the Status (twit) in the backend database
        """
        pass

    @abstractmethod
    def init_backend(self) -> None:
        """
        This method should do whatever is necessary to init the backend: connect, create tables, etc
        """
        pass
