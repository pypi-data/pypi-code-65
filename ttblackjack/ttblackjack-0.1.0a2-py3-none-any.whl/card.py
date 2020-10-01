from typing import List
from ttblackjack.suit import Suit


class Card:
    # joker not included.
    acceptable_vals = ['A'] + \
        [str(_) for _ in range(2, 11)] + \
        ['J', 'Q', 'K']

    def __init__(self, suit: Suit, val: str, face_up: bool=False) -> None:
        self.suit = suit
        self.val = val
        self.facing = 'UP' if face_up else 'DOWN'

    def __str__(self):
        # use 3 padding instead of 2, more visible
        return f'({self.suit}{self.val:>3})' if self.facing == 'UP' else '(? ??)'

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, v: str):
        v = v.upper() if v.isalpha() else v
        if v in self.acceptable_vals:
            self._val = v
        else:
            raise Exception(f'{v} not in {self.acceptable_vals}')

    @property
    def points(self) -> List:
        if self.val == 'A':
            return [1, 11]
        elif self.val in ('J', 'Q', 'K'):
            return [10, ]
        else:
            return [int(self.val), ]

    def face_up(self):
        self.facing = 'UP'

    def face_down(self):
        self.facing = 'DOWN'


def main():
    from ttblackjack import CLUB
    c1 = Card(CLUB, '10', True)
    print(c1)
    print(repr(c1))

    c2 = Card(CLUB, '10', False)
    print(c2)
    print(repr(c2))


if __name__ == "__main__":
    main()
