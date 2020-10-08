from minionize.cli import Row

import unittest


class TestRow(unittest.TestCase):
    def test_add_row(self):
        left = Row("abc", "")
        right = Row("def", "")
        r = left + right
        self.assertEqual("abc   def", r.title)
        self.assertEqual("", r.content)

    def test_add_row_content(self):
        left_content = """a
aa
aaa
aaaa
"""
        right_content = """bbbb
bbb
bb
b
"""
        left = Row("aaaaa", left_content)
        right = Row("bbbbb", right_content)
        r = left + right
        expected_content = """a       bbbb
aa      bbb
aaa     bb
aaaa    b"""
        self.assertEqual(expected_content, r.content)
