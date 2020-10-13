import json
from abc import ABC, abstractmethod
from typing import Dict, List, Union

from pandas import DataFrame


class SQLClient(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def switch_to(self, db_object, db_object_name):
        pass

    @abstractmethod
    def dml_query(self, query_string: str) -> None:
        pass

    @abstractmethod
    def select_query(self, query_string: str) -> DataFrame:
        pass

    @staticmethod
    def _load_configuration_file(configuration_file_path: str) -> Union[Dict, List]:
        with open(configuration_file_path, "r") as config_file:
            return json.load(config_file, strict=False)

    @classmethod
    def from_config_file(cls, file_path: str):
        """
        Alternate constructor allowing params to be specified via config file.

        :param file_path: Location of config file
        """
        config = cls._load_configuration_file(file_path)
        return cls(config)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.disconnect()
        # Returning True means we handled the exception, which we aren't.
        # We're just making sure resources get properly cleaned up
        return False
