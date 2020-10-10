from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict
import pandas as pd

T = TypeVar('T')

class IDataService(ABC, Generic[T]):

    @abstractmethod
    def add_or_update(self, obj_identifier: str, objs: List[T]) -> T:
        pass

    @abstractmethod
    def retrieve_data(self, obj_identifier: str, ids: List[str] = None) -> List[T]:
        pass

    @abstractmethod
    def delete(self, obj_identifier: str, ids: List[str]) -> Dict[str, bool]:
        pass

    @abstractmethod
    def translate_from_data_rows(self, df: pd.DataFrame) -> List[T]:
        pass
