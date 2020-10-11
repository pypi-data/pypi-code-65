from __future__ import annotations

import itertools
import random
from collections import defaultdict
from typing import Dict, Iterable, List, Set

import numpy as np

from .strategies import strategies
from .types import Index, PerfectSquare, Value


class Puzzle:
    """
    The object can be constructed with a 1-dimensional board:
    ```python
    arr_1d = [1, 0, 3, 4, 0, 4, 1, 0, 0, 3, 0, 1, 4, 0, 2, 3]
    puzzle = Puzzle(arr_1d, 0)
    ```
    ... or with a 2-dimensional board:
    ```python
    arr_2d = [[1, 0, 3, 4],
            [0, 4, 1, 0],
            [0, 3, 0, 1],
            [4, 0, 2, 3]]
    puzzle = Puzzle(arr_2d, 0)

    ```

    Args:
        list: An iterable representing a Sudoku board
        blank: The value used to represent a blank cell
    """

    class Tokens(list):
        __slots__ = tuple()

        def swap(self, i: Value, j: Value):
            self[i], self[j] = self[j], self[i]

        def shuffle(self):
            tokens = self[1:]
            random.shuffle(tokens)
            self[1:] = tokens

    class Cell:
        __slots__ = 'board', '__candidates'

        board: Puzzle
        __candidates: Set[Value]

        def __init__(self, board: Puzzle, value: Value):
            self.board = board
            self.candidates = set()
            self.value = value

        @property
        def candidates(self) -> Set[Value]:
            return self.__candidates

        @candidates.setter
        def candidates(self, candidates: Iterable):
            self.__candidates = set(candidates)

        @property
        def value(self) -> Value:
            if len(self.__candidates) > 1:
                return 0
            return next(iter(self.__candidates))

        @value.setter
        def value(self, value: Value):
            if value == 0:
                self.candidates = {i + 1 for i in range(self.board.order)}
            else:
                self.strip(value)

        def is_blank(self) -> bool:
            return len(self.__candidates) > 1

        def strip(self, *candidates: Iterable):
            before = len(self.candidates)
            self.candidates = candidates
            return before - len(self.candidates)

    __slots__ = 'order', 'tokens', 'cells'

    order: PerfectSquare
    tokens: Tokens
    cells: List[Cell]

    def _box(self, index: Index):
        boxWidth = int(self.order ** .5)
        row = index // self.order
        col = index % self.order
        edgeRow = boxWidth * (row // boxWidth)
        edgeCol = boxWidth * (col // boxWidth)

        for i in range(self.order):
            r = edgeRow + i // boxWidth
            c = edgeCol + (i % boxWidth)
            if not (r == row and c == col):
                p = int(self.order * r + c)
                yield p, self.cells[p]

    def _row(self, index: Index):
        row = index // self.order
        col = index % self.order

        for i in range(self.order):
            if i != col:
                p = int(self.order * row + i)
                yield p, self.cells[p]

    def _col(self, index: Index):
        row = index // self.order
        col = index % self.order

        for i in range(self.order):
            if i != row:
                p = int(self.order * i + col)
                yield p, self.cells[p]

    def _peers(self, index: Index):
        boxWidth = int(self.order ** .5)
        row = index // self.order
        col = index % self.order
        edgeM = boxWidth * (row // boxWidth)
        edgeN = boxWidth * (col // boxWidth)

        peers = set()

        for i in range(self.order):
            r = edgeM + i // boxWidth
            c = edgeN + i % boxWidth
            if i != col:
                p = int(self.order * row + i)
                if p not in peers:
                    yield p, self.cells[p]
                    peers.add(p)
            if i != row:
                p = int(self.order * i + col)
                if p not in peers:
                    yield p, self.cells[p]
                    peers.add(p)
            if not (r == row and c == col):
                p = int(self.order * r + c)
                if p not in peers:
                    yield p, self.cells[p]
                    peers.add(p)

    def _blank(self, indices=None):
        if indices is None:
            indices = range(self.order ** 2)
        for i in indices:
            cell = self.cells[i]
            if cell.is_blank():
                yield i, cell

    def has_conflicts(self) -> bool:
        """
        A method to determine if the board has any conflicting cells

        Returns:
            bool: True if the board has conflicts, False otherwise
        """
        for i, cell in enumerate(self.cells):
            if not cell.is_blank():
                for _, peer in self._peers(i):
                    if not peer.is_blank() and cell.value == peer.value:
                        return True
        return False

    def __init__(self, iterable: Iterable, blank):
        iterable = list(itertools.chain.from_iterable(iterable))

        self.order = int(len(iterable) ** .5)
        self.tokens = self.Tokens(blank)
        self.cells = np.empty(len(iterable), dtype=object)

        for i, token in enumerate(iterable):
            try:
                v = self.tokens.index(token)
            except ValueError:
                self.tokens.append(token)
                v = len(self.tokens) - 1
            self.cells[i] = self.Cell(self, v)

    def _shift_indices(self, *indices: List[Index]) -> None:
        tmp = self.cells[indices[0]]
        for i in range(1, len(indices)):
            self.cells[indices[i - 1]] = self.cells[indices[i]]
        self.cells[indices[-1]] = tmp

    def reflect(self, direction="horizontal") -> None:
        """
        Reflect the Sudoku board horizontally or vertically

        Args:
            direction (str): The direction in reflection
        """
        n = self.order
        x = n // 2
        y = n - 1
        if direction == "horizontal":
            for i in range(n):
                for j in range(x):
                    self._shift_indices(n * i + j, n * i + (y - j))
        else:
            for i in range(x):
                for j in range(n):
                    self._shift_indices(n * i + j, n * (y - i) + j)

    def rotate(self, rotations=1) -> None:
        """
        Rotate the Sudoku board clockwise a given number in times.

        Args:
            rotations (int): The number in clockwise rotations to be performed. This value may be negative and will be rounded.
        """
        if not isinstance(rotations, int):
            rotations = round(rotations)
        if rotations % 4 == 0:
            return
        elif rotations % 2 == 0:
            self.cells = np.flip(self.cells)
            return
        elif rotations < 0:
            self.rotate(-1 * rotations + 2)
        else:
            n = self.order
            x = n // 2
            y = n - 1
            for i in range(x):
                for j in range(i, y-i):
                    self._shift_indices(
                        n * i + j,
                        n * (y - j) + i,
                        n * (y - i) + y - j,
                        n * j + y - i
                    )

            self.rotate(rotations - 1)

    def transpose(self) -> None:
        """
        Switch the rows and columns in the Sudoku board
        """
        n = self.order
        for i in range(n):
            for j in range(i + 1, n):
                self._shift_indices(n * i + j, n * j + i)

    def shuffle(self) -> None:
        """
        Shuffle the board using rotations, reflections, and token-swapping
        """
        self.tokens.shuffle()
        for _ in range(self.order // 2):
            self.reflect(random.choice(("horizontal", "vertical")))
            self.rotate(random.choice(range(4)))

    def to_1D(self):
        """
        A method for getting back the Sudoku board as a 1-dimensional array

        Returns:
            A 1D array in the Sudoku board
        """
        return [self.tokens[c.value] for c in self.cells]

    def to_2D(self):
        """
        A method for getting back the Sudoku board as a 2-dimensional array

        Returns:
            A 2D array in the Sudoku board
        """
        return np.reshape(self.to_1D(), (self.order, self.order)).tolist()

    def to_string(self) -> str:
        """
        A method for getting back the Sudoku board as a string

        Returns:
            str: A string representation in the Sudoku board
        """
        return "".join(self.to_1D())

    def to_formatted_string(self,
                            cell_corner="┼",
                            box_corner="╬",
                            top_left_corner="╔",
                            top_right_corner="╗",
                            bottom_left_corner="╚",
                            bottom_right_corner="╝",
                            inner_top_tower_corner="╦",
                            inner_bottom_tower_corner="╩",
                            inner_left_floor_corner="╠",
                            inner_right_floor_corner="╣",
                            cell_horizontal_border="─",
                            box_horizontal_border="═",
                            cell_vertical_border="│",
                            box_vertical_border="║",
                            blank=" ") -> str:
        """
        A method for getting back the Sudoku board as a formatted string

        Returns:
            str: A formatted string representing the Sudoku board
        """
        unit = int(self.order ** .5)
        token_width = max([len(str(t)) for t in self.tokens])

        cell_width = token_width + 2
        box_width = unit * (cell_width + 1) - 1

        top_border = top_left_corner + box_horizontal_border * \
            (box_width) + (inner_top_tower_corner + box_horizontal_border *
                           (box_width)) * (unit - 1) + top_right_corner
        bottom_border = bottom_left_corner + box_horizontal_border * \
            (box_width) + (inner_bottom_tower_corner + box_horizontal_border *
                           (box_width)) * (unit - 1) + bottom_right_corner
        floor_border = inner_left_floor_corner + box_horizontal_border * \
            (box_width) + (box_corner + box_horizontal_border *
                           (box_width)) * (unit - 1) + inner_right_floor_corner
        bar_border = (box_vertical_border + cell_horizontal_border * (cell_width) + (cell_corner +
                                                                                     cell_horizontal_border * (cell_width)) * (unit - 1)) * (unit) + box_vertical_border

        formatted_str = f"{top_border}\n{box_vertical_border} "
        for i, c in enumerate(self.cells):
            v = c.value
            formatted_str += f"{self.tokens[v] if not c.is_blank() else blank} "
            if (i + 1) % (self.order * unit) == 0:
                if i + 1 == len(self.cells):
                    formatted_str += f"{box_vertical_border}\n{bottom_border}"
                else:
                    formatted_str += f"{box_vertical_border}\n{floor_border}\n{box_vertical_border} "
            elif (i + 1) % self.order == 0:
                formatted_str += f"{box_vertical_border}\n{bar_border}\n{box_vertical_border} "
            elif (i + 1) % unit == 0:
                formatted_str += f"{box_vertical_border} "
            else:
                formatted_str += f"{cell_vertical_border} "

        return formatted_str

    def is_solved(self) -> bool:
        """
        Check whether puzzle is solved
        """
        return not any(c.is_blank() for c in self.cells)

    def solve(self) -> Dict[str, int]:
        """
        Solve the puzzle with strategies
        """
        candidate_eliminations = defaultdict(int)

        if self.has_conflicts():
            return None

        while not self.is_solved():
            changed = False
            for strategy in strategies(self.order):
                eliminations = strategy(self)

                if eliminations > 0:
                    candidate_eliminations[strategy.name] += eliminations
                    changed = True
                    break
            if not changed:
                return dict(candidate_eliminations)

        return dict(candidate_eliminations)

    def has_solution(self) -> bool:
        """
        Return whether the puzzle can be solved using strategies
        """
        return bool(Puzzle(self.to_string(), self.tokens[0]).solve())

    def rate(self) -> float:
        """
        Calculate the difficulty of solving the puzzle

        Returns:
            float: A difficulty score between 0 and 1
        """
        if self.is_solved():
            return 0

        candidate_eliminations = Puzzle(self.to_1D(), self.tokens[0]).solve()
        if not candidate_eliminations:
            return -1

        difficulties = dict()
        for strat in strategies(self.order):
            difficulties[strat.name] = strat.difficulty

        difficulty = 0
        for strat in candidate_eliminations.keys():
            ds = difficulties[strat]
            cs = candidate_eliminations[strat]
            difficulty += ds * (cs / (self.order ** 3 - self.order ** 2))

        return difficulty
