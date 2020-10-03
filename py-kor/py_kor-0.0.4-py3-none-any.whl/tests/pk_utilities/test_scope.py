import unittest

from py_kor.pk_types import *
from py_kor.pk_utilities import Scope, EScope


class ScopeTestCase(unittest.TestCase):
    def setUp(self) -> None:

        def increment(value: MInteger) -> None:
            value += 1
            pass

        def decrement(value: MInteger) -> None:
            value -= 1
            pass

        self.increment = increment
        self.decrement = decrement

    def tearDown(self) -> None:
        pass

    def test_empty_scope(self) -> None:
        try:
            with Scope() as sc:
                pass
        except BaseException as e:
            self.assertTrue(False, f'Unexpected error: {e}')

    def test_enter_scope(self) -> None:
        test_value = MInteger(0)

        try:
            with Scope(on_enter=lambda: self.increment(test_value)) as sc:
                pass
        except BaseException as e:
            self.assertTrue(False, f'Unexpected error: {e}')

        self.assertEqual(test_value, 1)

    def test_exit_scope(self) -> None:
        test_value = MInteger(1)

        try:
            with Scope(on_enter=lambda: self.decrement(test_value)) as sc:
                pass
        except BaseException as e:
            self.assertTrue(False, f'Unexpected error: {e}')

        self.assertEqual(test_value, 0)


class EScopeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass
