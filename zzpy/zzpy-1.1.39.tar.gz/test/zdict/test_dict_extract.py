import unittest
from zzpy import dict_extract


class TestCase(unittest.TestCase):
    def test1(self):
        d1 = {
            "a": 1, "b": 2, "c": 3
        }
        d2 = dict_extract(d1, "a")
        self.assertDictEqual(d2, {"a": 1})

    def test2(self):
        d1 = {
            "a": 1, "b": 2, "c": 3
        }
        d2 = dict_extract(d1, "a")
        d2["a"] = 0
        self.assertEqual(d2["a"], 0)
        self.assertEqual(d1["a"], 1)

    def test3(self):
        d1 = {
            "a": 1, "b": 2, "c": 3
        }
        d2 = dict_extract(d1, "a", "b")
        self.assertDictEqual(d2, {"a": 1, "b": 2})

    def test4(self):
        d1 = {
            "a": 1, "b": 2, "c": 3
        }
        d2 = dict_extract(d1, ("a", "b"))
        self.assertDictEqual(d2, {"a": 1, "b": 2})

    def test5(self):
        d1 = {
            "a": 1, "b": 2, "c": 3
        }
        d2 = dict_extract(d1, {"a", "b"})
        self.assertDictEqual(d2, {"a": 1, "b": 2})

    def test6(self):
        d1 = {
            "a": 1, "b": 2, "c": 3
        }
        d2 = dict_extract(d1, ["a", "b"])
        self.assertDictEqual(d2, {"a": 1, "b": 2})
