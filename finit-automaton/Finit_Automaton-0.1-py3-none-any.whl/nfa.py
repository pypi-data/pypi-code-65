from typing import Dict, Any, Tuple, List, Union, Generator

from mypackage.StateFa import StateFa
from mypackage.dfa import Dfa
from mypackage.fa_interface import InterfaceFa


class Nfa(InterfaceFa):
    """
        Create non deterministic finite automaton
    """

    def __init__(self, automaton):
        """
        Init a attributes of automaton
        :param automaton :
        """
        self.__automaton = automaton
        self.__states: list = self._get_states()
        self.__alphabet: dict = self.__automaton["alphabet"]
        self.__dictionary: dict = self._dictionary()
        if self.__automaton["deterministic"]:
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

    def read(self, word: str) -> Union[bool, str]:
        """
        the firsts states determines the start of the automaton
        read set of symbols and determine this automaton accept this symbols
        :param word:
        :return boolean value :
        """
        start_sets = self._sets_start()
        try:
            casuistic = [self._read(word, i.state) for i in start_sets]
        except ValueError:
            return "No Has intraducido una cadena valida"
        return any(casuistic)

    def _read(self, word: str, state: int) -> bool:
        if len(word) == 0:
            return self.__states[state].is_final()
        char: str = word[0]
        if char not in self.__alphabet:
            raise ValueError
        for i in self.__dictionary[state][char]:
            return self._read(word[1:], i)
        return False

    def determine(self) -> Dfa:
        """
        Transform a non-deterministic automata to a deterministic
        :return: new Dfa
        """
        start = tuple(map(lambda x: x.state, self._start_state()))
        determined = self._determine(start)
        return self._to_dfa(determined)

    def _determine(self, key: Tuple, table=None) -> Dict:
        """
        Create table
        :param key:
        :param table:
        :return:
        """
        if table is None:
            table = {}
        if self._is_none_next_key(key):
            return table
        table[key] = self._morphs_key(key)
        for next_key in self._next_key_in_table(key, table):
            if next_key not in table:
                table = self._determine(next_key, table)
        return table

    def _morphs_key(self, key: tuple) -> dict:
        dictionary_morphs: Dict[Any, Tuple[Any, ...]] = {}
        for symbol in self.__alphabet:
            _set = set()
            for elem in key:
                morph = self.__dictionary[elem][symbol]
                _set.update(morph)
            dictionary_morphs[symbol] = tuple(_set)
        return dictionary_morphs

    def _to_dfa(self, dictionary_convert: dict) -> Dfa:
        return Dfa({'deterministic': True,
                    'alphabet': self.__alphabet,
                    'states': self._generate_list_states_dfa(dictionary_convert)
                    })

    def _generate_list_states_dfa(self, dic: dict) -> List[dict]:
        _list_keys = list(dic.keys())
        return [{'state': _list_keys.index(key),
                 'final': self._is_final_state(key),
                 'start': self._is_start_state(key),
                 'morphs': {s: _list_keys.index(dic[key][s])
                            for s in self.__alphabet}} for key in _list_keys]

    def _is_start_state(self, args: tuple) -> bool:
        for i in args:
            if not self.__states[i].is_start():
                return False
        return True

    def _is_final_state(self, args: Tuple) -> bool:
        for i in args:
            if self.__states[i].is_final():
                return True
        return False

    def _start_state(self) -> Tuple[Any, ...]:
        start_state = filter(lambda x: x.is_start(), self.__states)  # [x for x in self.__states if x.is_start()]
        return tuple(start_state)

    def _get_states(self) -> list:
        return [StateFa(i["state"],
                        i["final"],
                        i["start"],
                        i["morphs"]) for i in self.__automaton["states"]]

    def _dictionary(self) -> Dict:
        return {h.state: {j: tuple(h.morphs[j])
                          # uso de una tupla para key : las tuplas al
                          # ser inmutables pueden usarse como key
                          for j in self.__alphabet}
                for h in self.__states
                }

    @staticmethod
    def _is_none_next_key(next_key: Tuple) -> bool:
        return True if next_key is None else False

    @staticmethod
    def _get_values(next_key: Tuple, table: Dict) -> Tuple:
        return table[next_key].values()

    @staticmethod
    def _next_key(table: Dict, args: tuple) -> Union[None, Tuple]:
        for value in args:
            if value not in table:
                yield value
        yield None

    def _next_key_in_table(self, start, table):
        return self._next_key(table, self._get_values(start, table))

    def _sets_start(self) -> Generator[Any, Any, None]:
        return (x for x in self.__states if x.is_start())
