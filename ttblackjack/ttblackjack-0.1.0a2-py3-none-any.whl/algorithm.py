"""
    functions will be like:
    boofar(player, others, past, decks)->str:
        pass
"""
from typing import Sequence
from ttblackjack import Action
from ttblackjack.hand import Hand


DEALER_BUST = False


def user(**kwargs):
    prompt = \
        'Available actions:\n' \
        '1. Hit\n' \
        '2. Stand\n' \
        '>>> '
    while True:
        try:
            act = int(input(prompt))
            if act in (1, 2):
                break
        except Exception:
            pass
    if act == 1:
        return Action.hit
    elif act == 2:
        return Action.stand
    else:
        raise Exception(f'Unknown action {act}')


def dealer(hand: Hand=None, **kwargs):
    if DEALER_BUST:
        print('!! WARNGIN: DEALER_BUST !!')    # simulate dealer busted
        return Action.hit
    return Action.hit if hand.e_max < 17 else Action.stand    # stand on 17


def basic_1(hand: Hand=None, o_hands: Sequence[Hand]=None, past: Hand=None, decks: int=None, **kwargs):
    return Action.hit if hand.e_max < 16 else Action.stand
    pass


def basic_2(hand: Hand=None, o_hands: Sequence[Hand]=None, past: Hand=None, decks: int=None, **kwargs):
    return basic_1(hand=hand)
    pass


def x_ray(hand: Hand=None, o_hands: Sequence[Hand]=None, past: Hand=None, decks: int=None, **kwargs):
    return basic_1(hand=hand)
    pass


ALGORITHMS = {
    'user': user,
    'dealer': dealer,
    'basic 1': basic_1,
    'basic 2': basic_2,
    'x-ray': x_ray,
}
