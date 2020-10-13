import unittest


class TestCase(unittest.TestCase):
    def test(self):
        from zzpy import dict_recursive_get
        self.assertIsNone(dict_recursive_get({}, key=""))
        self.assertIsNone(dict_recursive_get({"k": 1}, key=""))
        self.assertEqual(dict_recursive_get({"k": 1, "": 2}, key=""), 2)
        self.assertIsNone(dict_recursive_get({"k": 1, "": 2}, key="."))
        self.assertEqual(dict_recursive_get({"k": 1, "": {"": 2}}, key="."), 2)
        self.assertEqual(dict_recursive_get({"k": 1, "a": {"b": 2}}, key="a.b"), 2)
        self.assertEqual(dict_recursive_get({"k": 1, "a": {}}, key="a.b", default_value=3), 3)
