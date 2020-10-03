"""Este es el docstring de mi_paquete"""
from __future__ import annotations

from typing import Tuple, List, Union, Dict

from PySimpleAutomata import automata_IO
from os import path
from mypackage.StateFa import StateFa
from mypackage.fa_interface import InterfaceFa


class Dfa(InterfaceFa):
    """
        Create deterministic finite automaton
    """

    def __init__(self, automaton):
        """
        Initialize a attributes of automaton
        :param automaton :
        """
        self.__automaton = automaton
        self.__states: list = sorted(self._get_states(), key=lambda x: x.state)
        self.__alphabet: dict = self.__automaton["alphabet"]
        self.__dictionary: dict = self._dictionary()
        if not self.__automaton["deterministic"]:
            raise TypeError

    @property
    def automaton(self):
        return self.__automaton

    @property
    def states(self):
        return self.__states

    @property
    def alphabet(self):
        return self.__alphabet

    @property
    def dictionary(self):
        return self.__dictionary

    def minimize(self) -> Dfa:
        """
        Initialize sets with final states and the others , generate _dictionary with the minimized automaton
        :return _dictionary:
        """

        initial_sets = self._final_or_not()
        automaton_minimized = self._minimize(initial_sets)
        minimized = self._put_the_morphs(automaton_minimized)
        return self._to_dfa(minimized)

    def read(self, word: str) -> Union[bool, str]:
        """
        the firsts states determines the start of the automaton
        :param word:
        :return boolean value :
        """
        start = self._sets_start()
        try:
            return self._read(word, start.state)
        except ValueError:
            return "No Has intraducido una cadena valida"

    def _dictionary(self) -> dict:
        """
        format a _dictionary
        :return _dictionary of states :
        """
        return {h.state: {j: h.morphs[j]
                          for j in self.__alphabet}
                for h in self.__states}

    def _read(self, word: str, state: int) -> bool:
        if len(word) == 0:
            return self.__states[state].is_final()

        char: str = word[0]
        if char not in self.__alphabet:
            raise ValueError  # introduction of non correct word
        next_state: int = self.__dictionary[state][char]
        return self._read(word[1:], next_state)  # recursive call (rest of word)

    def _final_or_not(self) -> Tuple[set, set]:
        finals_states = set(x for x in self.__states if x.is_final())
        non_final_states = finals_states ^ set(self.__states)
        finals_states = {x.state for x in finals_states}
        non_final_states = {x.state for x in non_final_states}
        return finals_states, non_final_states  # final{4,5,6,7,8}, non_final{0,1,2,3}

    def _sets_start(self) -> StateFa:
        for x in self.__states:
            if x.is_start():
                return x

    def _minimize(self, sets) -> list:
        category = []
        for i in sets:
            var = self._sets_generator(i)
            category = category + var  # union of sets in set1
        if sets != category:  # verify the changes of sets,
            return self._minimize(category)  # when the set is equal stop recursive call
        return category

    def _sets_generator(self, set_of_states: tuple) -> List[set]:
        out, in_ = self._divide_sets(set_of_states)
        if len(set_of_states) == 2 and len(out) == 2:
            return [{out.pop()}, out]
        if len(in_) == 0:
            return [out]
        if len(out) == 0:
            return [in_]
        return [in_, out]

    def _divide_sets(self, set_of_states: tuple) -> Tuple[set, set]:
        in_, out = set(), set()
        for i in set_of_states:
            for j in self.__dictionary[i]:
                if self.__dictionary[i][j] in set_of_states:
                    in_.add(i)
                else:
                    out.add(i)
                    in_.discard(i)
                    break
        return out, in_

    def _get_states(self) -> list:
        return [StateFa(i["state"],
                        i["final"],
                        i["start"],
                        i["morphs"])
                for i in self.__automaton["states"]]

    def _to_dfa(self, dict_automaton: Dict) -> Dfa:
        return Dfa(dict(deterministic=True,
                        alphabet=self.__alphabet,
                        states=[dict(state=key,
                                     final=self.__states[key].is_final(),
                                     start=self.__states[key].is_start(),
                                     morphs=dict_automaton[key]) for key in
                                dict_automaton]))

    def _put_the_morphs(self, lists):
        def exist(s):
            for i, j in enumerate(lists):
                if s in j:
                    return min(lists[i])

        minimized_dict = {}
        for elem in lists:
            if len(elem) == 1:
                minimized_dict[min(elem)] = {s: exist(self.__states[list(elem)[0]].morphs[s])
                                             for s in self.__alphabet}
            else:
                minimized_dict[min(elem)] = {x: min(elem)
                                             for x in self.__alphabet}
        return minimized_dict

    def __repr__(self):
        return self.__dictionary

    def __str__(self) -> str:
        return str(self.__repr__())

    def dot_dictionary(self, name: str) -> str:
        """
        Generate svg for automaton
        :param name:
        :param name of svg file:
        """
        dot = dict(initial_state=str(self._sets_start()),
                   alphabet=self.__alphabet, states={str(x.state) for x in self.__states},
                   accepting_states={str(x.state) for x in self.__states if x.is_final()},
                   transitions={(str(x.state), i): x.morphs[i]
                                for x in self.__states for i in self.alphabet})
        automata_IO.dfa_to_dot(dot, name, "../AF")
        while True:
            if path.exists(f"../AF/{name}.dot.svg"):
                return f"../AF/{name}.dot.svg"
