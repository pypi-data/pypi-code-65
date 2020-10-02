import rich.table as rt
from rich.console import Console
import random
from typing import (
    Tuple, List, Union
)


class Table:
    def __init__(self, headers: Union[List, Tuple], data: List[Union[List, tuple]] = None):
        example = random.choice(data)
        assert len(example) == len(headers), f"Header length {len(header)} " \
                                             f"not match data length {len(example)}"
        self._table_ = rt.Table(show_header=True, header_style="bold magenta")
        self.data = data
        self.headers = headers
        self.console = Console()
        for h in headers:
            self._table_.add_column(h, justify='right')
        for d in self.data:
            self._table_.add_row(*tuple(map(str, d)))

    def add_column(self, header: str):
        self._table_.add_column(header)
        self.headers.append(header)

    def add_row(self, data):
        self.data.append(data)

    def print(self):
        """Stdout."""
        # use rich to print table
        self.console.print(self._table_)

    def write(self, filepath: str):
        """Write to specific file."""
        with open(filepath, 'w') as fp:
            for header in self.headers:
                print(f"{header}", sep='\t', file=fp)
            print()
            for row in self.data:
                print(row, file=fp)


if __name__ == '__main__':
    data = [(i, 3 * j + 2) for i, j in enumerate(range(10, 20))]
    headers = ['x', 'y']
    table = Table(headers=headers, data=data)
    table.print()
