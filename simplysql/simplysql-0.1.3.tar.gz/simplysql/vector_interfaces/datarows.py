#! /usr/bin/python3.7.6
from typing import Tuple, List, Any
from simplysql.vector_interfaces.datarow import DataRow


class DataRows(object):
    def __init__(self, header: List[str], rows: List[Any], parent=None):
        self._header = header
        self._parent = parent
        self._rows = [DataRow(self.header(), row, index, self.parent)
                      for index, row in enumerate(rows)]

    @property
    def data(self) -> List[Any]:
        return [row.data for row in self._rows]

    @property
    def parent(self):
        return self._parent

    def header(self) -> List[str]:
        """
        Returns the list of column within the row.

        """
        return self._header

    def as_list(self) -> List[Any]:
        return self.data

    def as_tuple(self) -> Tuple[Any]:
        return tuple(map(tuple, self.data))

    def all(self) -> List[DataRow]:
        return self._rows

    def first(self) -> DataRow:
        return self[0]

    def last(self) -> DataRow:
        return self[-1]

    def count(self) -> int:
        return len(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __repr__(self) -> str:
        return "DataRows(count={})".format(len(self))

    def __iter__(self):
        index = 0

        while True:
            if index < self.count():
                yield self[index]
            else:
                return
            index += 1

    def __getitem__(self, index: int) -> DataRow:
        if isinstance(index, int):
            if index < 0:
                index = len(self) + index

            return self.all()[index]

        raise IndexError("DataRows has no index={}.".format(index))
