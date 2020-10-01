from typing import Sequence
from ttblackjack.card import Card


class Hand:
    """A sequence of Cards"""
    def __init__(self, cards=None) -> None:
        self.cards = [] if cards is None else cards

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        retval = []
        for card in self.cards:
            retval.append(str(card))
        return ' '.join(retval)

    def append(self, card: Card):
        self.cards.append(card)

    def extend(self, cards: Sequence):
        self.cards.extend(cards)

    def dump(self) -> Sequence:
        cards = self.cards
        self.cards = []
        assert len(cards) > 0, 'Sanity check.'
        return cards

    def pop(self) -> Card:
        """ Used by shoebox """
        return self.cards.pop(0)

    def split(self):
        """ Split hand. """
        raise Exception('Not implemented.')

    @property
    def is_empty(self) -> bool:
        return True if len(self.cards) == 0 else False

    @property
    def is_blackjack(self) -> bool:
        return self.e_max == 21

    @property
    def is_busted(self) -> bool:
        return self.e_max is None

    @property
    def e_max(self):
        """Effective max, largest points less than or equal to 21"""
        ep = self.every_points()
        possible = sorted([p for p in ep if p <= 21])

        if len(possible) == 0:    # all is > 21, busted
            return None
        return possible[-1]    # the largest

    def every_points(self):
        if self.is_empty:
            return [0, ]

        elif 'A' not in [c.val for c in self.cards]:
            accu = sum([c.points[0] for c in self.cards])
            return [accu, ]

        else:
            # i.e. [[1, 11], [1, 11], ...]
            A = [c.points for c in self.cards if c.val == 'A']
            assert len(A) > 0, f"There is no 'A', {A}"

            # points of cards that are not 'A',
            # i.e. [2, 3, 4, ...10, 10, 10, 10]
            nonA = [c.points[0] for c in self.cards if c.val != 'A']

            retval = []
            for i in range(0, len(A) + 1):
                retval.append(sum(nonA) + len(A) + 10 * i)

            return retval


"""
    Todo:
        add "natural/blackjack" check for bonus points
"""
