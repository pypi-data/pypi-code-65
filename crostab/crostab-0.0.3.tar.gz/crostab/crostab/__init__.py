import json
from dataclasses import dataclass

from veho.columns import column
from veho.matrix import init, mapper, shallow, transpose

from crostab.enum.keys import HEAD, ROWS, SIDE, TITLE
from crostab.types import Matrix


@dataclass
class Crostab:
    side: list
    head: list
    rows: Matrix
    title: str

    # __slots__ = (SIDE, HEAD, ROWS, TITLE)

    def __init__(self, side, head, rows, title=None, **rest):
        self.side = side
        self.head = head
        self.rows = rows
        self.title = title if title is None else ''
        if len(rest):
            for key, value in rest.items():
                self.__dict__[key] = value

    @staticmethod
    def ini(side, head, mapper_on_coordinate, title):
        rows = init(len(side), len(head), mapper_on_coordinate)
        return Crostab(side, head, rows, title)

    def to_dict(self): return {
        SIDE: self.side,
        HEAD: self.head,
        ROWS: self.rows,
        TITLE: self.title
    }

    def to_json(self): return json.dumps(self.to_dict())

    def map(self, fn):
        rows = mapper(self.rows, fn)
        return self.copy(self.side, self.head, rows, self.title)

    def cell(self, r, c):
        return self.rows[x][y] \
            if (x := self.roin(r)) >= 0 and (y := self.coin(c)) >= 0 \
            else None

    def element(self, x, y): return self.rows[x][y]

    @property
    def height(self): return len(self.side)

    @property
    def width(self): return len(self.head)

    def roin(self, field):
        try: return self.side.index(field)
        except ValueError: return -1

    def coin(self, field):
        try: return self.head.index(field)
        except ValueError: return -1

    def row(self, side_field):
        return self.rows[x] if (x := self.roin(side_field)) >= 0 else None

    def column(self, head_field):
        return column(self.rows, y) if (y := self.coin(head_field)) >= 0 else None

    def set_row(self, side_field, new_row):
        if (x := self.roin(side_field)) < 0: return self
        self.rows[x] = new_row
        return self

    def set_column(self, head_field, new_column):
        if (y := self.coin(head_field)) < 0: return self
        for i, row in enumerate(self.rows): row[y] = new_column[i]
        return self

    def set_row_by(self, side_field, fn):
        if (x := self.roin(side_field)) < 0: return self
        self.rows[x] = [fn(x) for x in self.rows[x]]
        return self

    def set_column_by(self, head_field, fn):
        if (y := self.coin(head_field)) < 0: return self
        for i, row in enumerate(self.rows): row[y] = fn(row[y])
        return self

    def transpose(self, title=None, mutate=True):
        return self.boot(side=self.head, head=self.side, rows=transpose(self.rows), title=title, mutate=mutate)

    def boot(self, side=None, head=None, rows=None, title=None, mutate=True):
        if not mutate: return self.copy(side, head, rows, title)
        if side: self.side = side
        if head: self.head = head
        if rows: self.rows = rows
        if title: self.title = title
        return self

    def copy(self, side=None, head=None, rows=None, title=None):
        if not side: side = self.side[:]
        if not head: head = self.head[:]
        if not rows: rows = shallow(self.rows)
        if not title: title = self.title
        return Crostab(side, head, rows, title)
