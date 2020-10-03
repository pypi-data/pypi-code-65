import unittest

from mypackage.dfa import Dfa
import json


def read_automaton():
    with open("../json/dfa.json", "r") as f:
        return json.load(f)


class TestDfa(unittest.TestCase):

    def test_Dictionary(self):
        correct_dict = {0: {'a': 1, 'b': 2}, 1: {'a': 3, 'b': 5},
                        2: {'a': 3, 'b': 2}, 3: {'a': 3, 'b': 4},
                        4: {'a': 3, 'b': 2}, 5: {'a': 6, 'b': 7},
                        6: {'a': 6, 'b': 5}, 7: {'a': 6, 'b': 7}}
        dfa = Dfa(read_automaton())
        self.assertEqual(correct_dict, dfa.dictionary)

    def test_Minimize(self):
        correct_sets = [{0}, {1}, {2}, {3}, {4}, {5, 6, 7}]
        dfa = Dfa(read_automaton())
        comparative = all(map(lambda x:
                              True if x in correct_sets
                              else False,
                              dfa._minimize(dfa._final_or_not())))
        self.assertTrue(comparative)

    def test_Put_morph(self):
        correct_dict = {0: {'a': 1, 'b': 2}, 1: {'a': 3, 'b': 5},
                        2: {'a': 3, 'b': 2}, 3: {'a': 3, 'b': 4},
                        4: {'a': 3, 'b': 2}, 5: {'a': 5, 'b': 5}}
        dfa = Dfa(read_automaton())
        set_minimized = dfa._minimize(dfa._final_or_not())
        complete_dfa = dfa._put_the_morphs(set_minimized)
        self.assertEqual(complete_dfa, correct_dict)


if __name__ == '__main__':
    unittest.main()
