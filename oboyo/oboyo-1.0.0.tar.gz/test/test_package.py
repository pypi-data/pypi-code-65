"""Tests package."""

import sys
from oboyo.calc import Calc, Distance


if sys.version_info[0] >= 3:
    import pytest

    def test_add():
        assert Calc().add(2, 3) == 5, 'Should be 5'


    def test_mul():
        assert Calc().multiply(2, 3) == 6, 'Should be 6'


    def test_power():
        assert Distance(2).power(2) == 4, 'Should be 4'

else:
    import unittest

    class TestCode(unittest.TestCase):

        def test_add(self):
            self.assertEqual(Calc().add(2, 3), 5, "Should be 5")

        def test_mul(self):
            self.assertEqual(Calc().multiply(2, 3), 6, "Should be 6")

        def test_power(self):
            self.assertEqual(Distance(2).power(2), 4, "Should be 4")

    if __name__ == '__main__':
        unittest.main()
