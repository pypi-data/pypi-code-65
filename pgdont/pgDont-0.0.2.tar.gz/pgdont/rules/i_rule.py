from abc import ABC, abstractmethod
from typing import Dict, List

from psycopg2._psycopg import connection as Connection


class IRule(ABC):

    def __init__(self, connection: Connection):
        self.connection = connection

        self.infos = {
            "rule": self.__class__.__name__,
            "url": self.url,
            "details": None,
        }

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def process(self) -> Dict:
        pass
