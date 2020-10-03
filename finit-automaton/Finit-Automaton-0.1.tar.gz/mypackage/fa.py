from mypackage.dfa import Dfa
from mypackage.nfa import Nfa
from mypackage.fa_interface import InterfaceFa


class Fa(InterfaceFa):
    def __init__(self, automaton):
        self.__automaton = automaton
        if self.automaton["deterministic"]:
            self.heritage = Dfa(automaton)
        elif not self.automaton["deterministic"]:
            self.heritage = Nfa(automaton)
        else:
            raise TypeError

    def read(self, word):
        return self.heritage.read(word)

    @property
    def automaton(self):
        return self.__automaton

    @property
    def states(self):
        return self.heritage.states

    @property
    def alphabet(self):
        return self.heritage.alphabet

    @property
    def dictionary(self):
        return self.heritage.dictionary

    def __repr__(self):
        return self.heritage.dictionary

    def __str__(self):
        return self.heritage.__str__()
