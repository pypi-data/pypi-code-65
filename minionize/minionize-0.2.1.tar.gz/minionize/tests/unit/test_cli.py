from minionize.cli import Section, Row

import unittest


class TestRow(unittest.TestCase):
    def test_add_sections(self):
        left = Section("abc")
        right = Section("def")
        r = Row([left, right], margin=3)
        self.assertEqual("abc   def", str(r).strip())

    def test_add_section_more_content(self):
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
        left = Section(left_content)
        right = Section(right_content)
        r = Row([left, right], margin=3)
        expected_content = """a      bbbb
aa     bbb
aaa    bb
aaaa   b"""
        self.assertEqual(expected_content, str(r).strip())
