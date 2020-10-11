
import itertools

from .types import PerfectSquare


class Strategy:
    """
    Also known as a [Solving Technique](http://sudopedia.enjoysudoku.com/Solving_Technique.html)
    """
    __slots__ = 'name', 'difficulty'

    name: str
    difficulty: float

    def __init__(self, name=None, difficulty=None):
        self.name = name if name is not None else self.__class__.__name__
        self.difficulty = difficulty


class RefreshCandidates(Strategy):
    """
    Remove invalid candidates from each cell
    """

    def __init__(self):
        super().__init__(difficulty=0.769)

    def __call__(self, puzzle):
        candidate_eliminations = 0
        for i, cell in enumerate(puzzle.cells):
            for _, peer in puzzle._peers(i):
                if cell.is_blank() and not peer.is_blank():
                    if peer.value in cell.candidates:
                        cell.candidates.remove(peer.value)
                        candidate_eliminations += 1
        return candidate_eliminations


class HiddenSubset(Strategy):
    """
    Apply the [Hidden Subset](http://sudopedia.enjoysudoku.com/Hidden_Subset.html) strategy
    """

    __slots__ = ('size',)

    size: int

    def __init__(self, size):
        super().__init__(difficulty=0.163 * size)
        self.name += f" - {size}"
        self.size = size

    def __call__(self, puzzle):
        if self.size <= 0 or self.size >= puzzle.order:
            return 0

        complement_size = puzzle.order - self.size
        if complement_size < self.size:
            return NakedSubset(complement_size)(puzzle)

        candidate_eliminations = 0
        for b, blank in puzzle._blank():
            if len(blank.candidates) >= self.size:
                for house in [puzzle._row, puzzle._col, puzzle._box]:
                    for hidden_candidates in itertools.combinations(blank.candidates, self.size):
                        subset = set(
                            p for p, peer in house(b) if (
                                any((hc in peer.candidates)
                                    for hc in hidden_candidates)
                            )
                        )
                        subset.add(b)

                        if len(subset) == self.size:
                            for s in subset:
                                candidate_eliminations += puzzle.cells[s].strip(
                                    *hidden_candidates)

        return candidate_eliminations


class HiddenSingle(HiddenSubset):
    """
    The [Hidden Single](http://sudopedia.enjoysudoku.com/Hidden_Single.html) strategy
    """

    def __init__(self):
        super().__init__(1)


"""
Alias for the [[HiddenSingle]] strategy
"""
PinnedDigit = HiddenSingle


class NakedSubset(Strategy):
    """
    Apply the [Naked Subset](http://sudopedia.enjoysudoku.com/Naked_Subset.html) strategy
    """
    __slots__ = ("size",)

    def __init__(self, size):
        super().__init__(difficulty=0.323 * size)
        self.name += f" - {size}"
        self.size = size

    def __call__(self, puzzle):
        if self.size <= 0 or self.size >= puzzle.order:
            return 0

        complement_size = puzzle.order - self.size
        if complement_size < self.size:
            return HiddenSubset(complement_size)(puzzle)

        candidate_eliminations = 0
        for b, blank in puzzle._blank():
            if len(blank.candidates) == self.size:
                for house in [puzzle._row, puzzle._col, puzzle._box]:
                    complement = set(
                        p for p, peer in house(b) if (
                            len(peer.candidates) > self.size
                            or
                            any(
                                (pc not in blank.candidates)
                                for pc in peer.candidates
                            )
                        )
                    )
                    if len(complement) == complement_size:
                        for p in complement:
                            for c in blank.candidates:
                                if c in puzzle.cells[p].candidates:
                                    puzzle.cells[p].candidates.remove(c)
                                    candidate_eliminations += 1

        return candidate_eliminations


class NakedSingle(NakedSubset):
    """
    The [Naked Single](http://sudopedia.enjoysudoku.com/Naked_Single.html) strategy
    """

    def __init__(self):
        super().__init__(1)


"""
Alias for the [[NakedSingle]] strategy
"""
ForcedDigit = NakedSingle

"""
Alias for the [[NakedSingle]] strategy
"""
SoleCandidate = NakedSingle


class NakedDouble(NakedSubset):
    """
    Apply the [Naked Double](http://sudopedia.enjoysudoku.com/Naked_Double.html) strategy
    """

    def __init__(self):
        super().__init__(2)


class NakedTriple(NakedSubset):
    """
    Apply the [Naked Triple](http://sudopedia.enjoysudoku.com/Naked_Triple.html) strategy
    """

    def __init__(self):
        super().__init__(3)


class NakedQuad(NakedSubset):
    """
    Apply the [Naked Quad](http://sudopedia.enjoysudoku.com/Naked_Quad.html) strategy
    """

    def __init__(self):
        super().__init__(4)


def strategies(order: PerfectSquare):
    """
    Generator for strategies from simple to complex with a given order
    """
    yield RefreshCandidates()
    for s in range(1, order // 2):
        yield NakedSubset(s)
        yield HiddenSubset(s)
