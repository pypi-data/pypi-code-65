from abc import ABC, abstractmethod
from ..types import Credentials


class ILoader(ABC):

    @abstractmethod
    def parse(self) -> Credentials:
        """Parses the credentials and returns a credential object"""
        pass
