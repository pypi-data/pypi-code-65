import unittest

from py_kor.pk_types import *


class MBooleanTestCase(unittest.TestCase):
    def test_operand(self):
        test_value_true = MBoolean(True)
        test_value_false = MBoolean(False)

        self.assertEqual(test_value_true, test_value_true)
        self.assertEqual(test_value_true, True)
        self.assertEqual(True, test_value_true)

        self.assertEqual(test_value_false, test_value_false)
        self.assertEqual(test_value_false, False)
        self.assertEqual(False, test_value_false)

        self.assertNotEqual(test_value_false, test_value_true)
        self.assertNotEqual(test_value_true, test_value_false)
        self.assertNotEqual(test_value_false, True)
        self.assertNotEqual(False, test_value_true)

        self.assertGreater(test_value_true, test_value_false)
        self.assertGreater(test_value_true, False)
        self.assertGreater(True, test_value_false)

        self.assertGreaterEqual(test_value_true, test_value_false)
        self.assertGreaterEqual(test_value_true, False)
        self.assertGreaterEqual(True, test_value_false)

        self.assertLess(test_value_false, test_value_true)
        self.assertLess(test_value_false, True)
        self.assertLess(False, test_value_true)

        self.assertLessEqual(test_value_false, test_value_true)
        self.assertLessEqual(test_value_false, True)
        self.assertLessEqual(False, test_value_true)
