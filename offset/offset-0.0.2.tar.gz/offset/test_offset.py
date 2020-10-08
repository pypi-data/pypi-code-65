import unittest
from text_shifter import TextShifter

class TestTextShifter(unittest.TestCase):

    def test_convert(self):
        tests = [
            {
                'params': {'text': 'hello, world!', 'number': 1},
                'expected': 'ifmmp-!xpsme"',
            },
            {
                'params': {'text': 'bcde', 'number': -1},
                'expected': 'abcd',
            },
        ]
        for test in tests:
            self.assertEqual(
                test.get('expected'),
                TextShifter.convert(**test.get('params'))
            )
