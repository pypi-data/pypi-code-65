#! /usr/bin/python3.7.6
from typing import Tuple, List, Dict, Any


class DataColumn(object):
    def __init__(self, header: str, col_data: List[Any], index: int = 0, parent=None):
        self._header = header
        self._data = list(col_data)
        self._index = index
        self._parent = parent

    @property
    def data(self) -> List[Any]:
        return self._data

    @property
    def index(self) -> int:
        return self._index

    @property
    def parent(self) -> Any:  # DataColumns
        return self._parent

    def header(self) -> str:
        """
        Returns the column header

        """
        return self._header

    def as_list(self) -> List[Any]:
        return [self.header(), self.data]

    def as_dict(self) -> Dict[str, Any]:
        return {self.header(): self.data}

    def as_tuple(self) -> Tuple:
        return (self.header(), tuple(self.data))

    def __getitem__(self, name) -> Any:  # DataColumn
        # get item --> index-based
        if isinstance(name, int):
            return self.data[name]

        # get item --> string-based
        if name in self.header():
            index = self.header().index(name)
            if self.header().count(name) > 1:
                raise KeyError("DataColumn has multiple keys={}.".format(name))
            return self.data[index]

        raise KeyError("DataColumn has no name={}.".format(name))

    def __repr__(self) -> str:
        return "DataColumn(index={})".format(self.index)
