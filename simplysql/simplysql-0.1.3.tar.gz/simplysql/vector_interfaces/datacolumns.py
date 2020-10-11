#! /usr/bin/python3.7.6
from typing import Tuple, List, Any

from simplysql.vector_interfaces.datacolumn import DataColumn


class DataColumns(object):
    def __init__(self, header: List[str], columns: List[Any], parent=None):
        self._header = header
        self._parent = parent
        self._data = list(map(list, zip(*columns)))
        self._cols = [DataColumn(self.header()[index], col, index,
                                 self.parent) for index, col in enumerate(self._data)]

    @property
    def data(self) -> List[Any]:
        return self._data

    @property
    def parent(self) -> Any:  # DataTable
        return self._parent

    def as_list(self) -> List[Any]:
        return list(map(list, self.data))

    def as_tuple(self) -> Tuple[Any]:
        return tuple(map(tuple, self.data))

    def header(self) -> str:
        """
        Returns the list of column within the row.

        """
        return self._header

    def all(self) -> List[DataColumn]:
        return self._cols

    def first(self) -> DataColumn:
        return self[0]

    def last(self) -> DataColumn:
        return self[-1]

    def count(self) -> int:
        return len(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        i = 0

        while True:
            if i < self.count():
                yield self[i]
            else:
                return
            i += 1

    def __getitem__(self, index) -> DataColumn:
        if isinstance(index, int):
            if index < 0:
                index = len(self) + index

            return self.all()[index]

        raise IndexError("DataColumns has no index={}.".format(index))

    def __repr__(self):
        return "DataColumns(count={})".format(len(self))
