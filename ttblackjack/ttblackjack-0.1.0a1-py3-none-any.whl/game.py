"""
    Enable card counting.
    Shuffle logic:
        Continuous Shuffle Machine?
            Shuffle every half deck?
        Shuffle on before using last 52 cards.

    rename Game.sink to Game.discard_tray

"""
import random
import sys
import time
from ttblackjack.card import Card
from ttblackjack import INSTRUCTIONS
from ttblackjack import Action, CLUB, DIAMOND, HEART, SPADE
from ttblackjack.hand import Hand
from ttblackjack.player import Player
from ttblackjack.algorithm import ALGORITHMS


RSLEEP = True    # debug: real sleeep instead of print sleep


class Game:

    def __init__(self,
                 decks, sleep, rounds,
                 yes, viewer, debug, assist,
                 players, shoebox, sink) -> None:
        self.decks: int = decks
        self.sleep: float = sleep
        self.rounds: int = rounds
        self.yes: bool = yes

        self.viewer: str = viewer
        self.assist: bool = assist
        self.debug: bool = debug

        self.players: list = players
        self.shoebox: Hand = shoebox

        self.sink = sink

    @classmethod
    def from_config(cls, config):
        decks = int(config['decks'])
        sleep = float(config['sleep'])
        rounds = int(config['rounds'])
        yes = bool(config['yes'])
        viewer = config['viewer']
        assist = bool(config['assist'])
        debug = bool(config['debug'])
        players = Game.get_players(config)
        shoebox = Game.get_shoebox(decks, shuffle=True, debug=debug)
        sink = Hand()

        return cls(
            decks=decks, sleep=sleep,
            rounds=rounds, yes=yes,
            viewer=viewer, assist=assist, debug=debug,
            players=players, shoebox=shoebox,
            sink=sink)

    @staticmethod
    def get_players(config):
        """ validate players and make them """
        """ later: parse config file elsewhere """
        if config['players'][-1]['algorithm'] != 'dealer':
            print('Last player must be dealer')
            sys.exit(1)

        players = []
        for p_conf in config['players']:
            algo = p_conf['algorithm']
            if algo not in ALGORITHMS.keys():
                print(f'{algo} is not an acceptable algorithm, choose from {ALGORITHMS}')
                sys.exit(1)

            is_user = True if algo == 'user' else False
            is_dealer = True if algo == 'dealer' else False
            p = Player(p_conf['name'], algo, is_user, is_dealer)
            players.append(p)

        return players

    @staticmethod
    def get_shoebox(decks, shuffle=True, debug=False) -> Hand:
        """ Hand object, fill it """
        cards = []

        for _d in range(decks):
            for suit in (CLUB, DIAMOND, HEART, SPADE):
                for v in Card.acceptable_vals:
                    cards.append(Card(suit, v, debug))
        assert len(cards) == decks * 52, 'My Maths are bad'

        if shuffle:
            random.shuffle(cards)

        return Hand(cards)

    def welcome(self):
        if self.debug:
            print('!! WARNING: Running in debug/x-ray mode !!')
        print()
        print('-- Welcome --')
        print(INSTRUCTIONS)
        print('-------------')
        if not self.yes:
            try:
                input('(Enter)')
            except KeyboardInterrupt:
                print('exit')
                sys.exit(0)

    def _round_start(self):
        """ distribute cards and stuff """
        for p in self.players:
            assert len(p.hand) == 0, f'Player {p} hand is not empty: {p.hand}'

        # distribute cards (face up)
        for p in self.players:
            card = self.shoebox.pop()
            card.face_up()
            p.hand.append(card)

        # distribute cards (face down)
        for p in self.players:
            card = self.shoebox.pop()
            card.face_down() if p.is_dealer else card.face_up()
            if self.debug:
                card.face_up()
            p.hand.append(card)

    def _round_end(self):
        """ used cards to sink and stuff """
        # collect into sink
        for p in self.players:
            cards = p.hand.dump()
            self.sink.extend(cards)

        for p in self.players:
            assert len(p.hand) == 0, f'Player {p} hand is not empty: {p.hand}'

    def _view_round_1(self, curr_player=None):
        """ viewer """
        print('-' * 20)
        for p in self.players:

            hint = '* ' if p == curr_player else '  '
            e_max = 'BUST' if p.hand.is_busted else p.hand.e_max

            if self.debug or curr_player is None:  # debug or round finished
                print(f'{hint}{p.name:<20}{e_max:<6}{p.hand}')

            elif p == self._get_dealer():  # hide dealer
                print(f'{hint}{p.name:<20}{" "*6}{p.hand}')

            elif self.assist:   # in talk
                e_max = 'BUST' if p.hand.is_busted else p.hand.e_max
                print(f'{hint}{p.name:<20}{e_max:<6}{p.hand}')

            else:
                print(f'{hint}{p.name:<20}{p.hand}')

        print('-' * 20)

        if self.debug:
            print('x-ray: ')
            for _i in range(5):
                print(str(self.shoebox.cards[_i]), end=' ')
            print('\n', '-' * 20)

    def _talk(self):
        """ Conversation between dealer and players """
        for p in self.players:

            if p.is_dealer:
                p.hand.cards[-1].face_up()

            while True:

                self._view_round_1(p)

                # check player hand here
                if p.hand.is_blackjack:
                    print(f'{p.name} BLACKJACK !!')
                    break

                if p.hand.is_busted:
                    print(f'{p.name} BUST !!')
                    break

                self._sleep()

                act = ALGORITHMS[p.algo](hand=p.hand)

                if act == Action.hit:
                    self._player_hit(p)
                    time.sleep(self.sleep)
                    # print('^^ SLEEP HERE ^^')

                elif act == Action.stand:
                    print(f'{p.name} Stand...')
                    break

                else:
                    raise Exception(f'Unknown action: {act}')

            self._sleep()

            print('\n= = =\n')

    def _results(self):
        print('Last View:')
        self._view_round_1()

        self._round_stats()
        self._game_stats()

    def _get_dealer(self):
        try:
            return [p for p in self.players if p.is_dealer][0]
        except IndexError:
            print('Cannot find dealer')
            sys.exit(1)

    def _round_stats(self):
        round_stats = {'win': [], 'push': [], 'lose': []}

        dealer = self._get_dealer()

        # calc
        for p in self.players:
            if p == dealer:    # don't conut dealer
                continue

            if (not p.hand.is_busted     # player not busted
                    and dealer.hand.is_busted):      # dealer busted
                round_stats['win'].append(p)
                p.score['win'] += 1

            elif (p.hand.is_busted                 # busted
                    or p.hand.e_max < dealer.hand.e_max):    # lower than dealer, e_max ?= None
                round_stats['lose'].append(p)
                p.score['lose'] += 1

            elif p.hand.e_max == dealer.hand.e_max:    # push
                # put later because both might be busted, e_max ?= None
                round_stats['push'].append(p)
                p.score['push'] += 1

            elif p.hand.e_max > dealer.hand.e_max:    # wins
                # put later because both might be busted, e_max ?= None
                round_stats['win'].append(p)
                p.score['win'] += 1

            else:
                breakpoint()
                raise Exception('Unknown result', )

        # round stats
        print('Round Stats:')
        for k, pl in round_stats.items():
            print(f'{k:<6}: {", ".join([p.name for p in pl])}')

    def _game_stats(self):
        print('= ' * 10)

        for p in self.players:
            print(f'{p.name:<15} {p.score_text}')

        print('= ' * 10)

    def _player_hit(self, p: Player):
        print(f'{p.name} Hit...')
        card = self.shoebox.pop()
        card.face_up()
        p.hand.append(card)

    def run(self):
        try:
            for round_ in range(self.rounds):
                print(f'Round: {round_+1}/{self.rounds}')
                self._round_start()
                self._talk()
                self._results()
                self._round_end()
                input('Next Round? (Or Ctrl+C to end)') if (not self.yes and round_ + 1 != self.rounds) else None
                print('\n' * 3)
            print('Done')
        except KeyboardInterrupt:
            print('\nexit\n')
            print('Thanks for playing')
            self._game_stats()
            return

    def _sleep(self, t=None):
        if RSLEEP:
            if t is None:
                time.sleep(self.sleep)
            else:
                time.sleep(float(t))
        else:
            print('^^ SLEEP HERE ^^')
