"""
    Later:
    remove state and implement Hand.state
    Implement 3: 'DOUBLE_DOWN', 4: 'SURRENDER'
    Implement MiniRound for calculating risk against dealer.
        Let player observe dealer's hand.
"""
from ttblackjack.hand import Hand


class Player:

    def __init__(self,
                 name, algo,
                 is_user=False, is_dealer=False
                 ) -> None:
        self.name = name
        self.algo = algo
        self.hand = Hand()    # can only have 1 hand
        self.is_user, self.is_dealer = is_user, is_dealer

        self.score = {'win': 0 if not self.is_dealer else '$',
                      'push': 0 if not self.is_dealer else '$',
                      'lose': 0 if not self.is_dealer else '$'}

    def __str__(self) -> str:
        return f'={self.name}:{self.algo}:{"user" if self.is_user else "dealer" if self.is_dealer else "npc"}:{len(self.hand)}='

    @property
    def score_text(self):
        return f'win: {self.score["win"]:<4} push: {self.score["push"]:<4} lose: {self.score["lose"]:<4}'
