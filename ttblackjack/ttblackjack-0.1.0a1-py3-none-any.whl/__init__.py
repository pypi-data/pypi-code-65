import sys
from pathlib import Path

import toml

from ttblackjack.suit import Suit


__version__ = "0.1.0.a1"
APP_NAME = 'ttblackjack'
PROJ_DIR = Path(__file__).parent.parent.resolve()
APP_DIR = Path(PROJ_DIR, APP_NAME).resolve()
CONFIG_FP = Path(APP_DIR, 'config.toml').resolve()

CLUB = Suit('Club', '♣')
DIAMOND = Suit('Diamond', '♦')
HEART = Suit('Heart', '♥')
SPADE = Suit('Spade', '♠')


class Action:
    hit = 'HIT'
    stand = 'STAND'


class InvalidConfigError(Exception):
    def __init__(self, message=None, errors=None) -> None:
        self.message = message
        self.errors = errors

    def __str__(self) -> str:
        if self.message:
            return f'InvalidConfigError: {self.message}'
        return 'InvalidConfigError'


def check_config(config):
    """Not Implemented"""
    pass


try:
    CONFIG = toml.load(CONFIG_FP)
    check_config(CONFIG)
except toml.TomlDecodeError:
    print('Cannot load config at:', CONFIG_FP)
    sys.exit(1)


INSTRUCTIONS = """\
Rules:
If the player is dealt an Ace and a ten-value card (called a
"blackjack" or "natural"), and the dealer does not, the player wins
and usually receives a bonus.

If the player exceeds a sum of 21 ("busts"), the player loses, even
if the dealer also exceeds 21.

If the dealer exceeds 21 ("busts") and the player does not, the
player wins.

If the player attains a final sum higher than the dealer and does
not bust, the player wins.

If both dealer and player receive a blackjack or any other hands
with the same sum called a "push", no one wins.\
"""

"""
Rules (source: https://en.wikipedia.org/wiki/Blackjack#Rules):

    If the player is dealt an Ace and a ten-value card (called a
    "blackjack" or "natural"), and the dealer does not, the player wins
    and usually receives a bonus.

    If the player exceeds a sum of 21 ("busts"), the player loses, even
    if the dealer also exceeds 21.

    If the dealer exceeds 21 ("busts") and the player does not, the
    player wins.

    If the player attains a final sum higher than the dealer and does
    not bust, the player wins.

    If both dealer and player receive a blackjack or any other hands
    with the same sum called a "push", no one wins.

Terminologies (source: http://www.casinostrategy.org/blackjack/blackjack-terminology.htm):
    use this, rename outhers later

"""
