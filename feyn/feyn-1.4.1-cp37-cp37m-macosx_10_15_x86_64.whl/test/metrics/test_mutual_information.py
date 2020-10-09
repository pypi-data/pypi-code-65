import unittest
import pytest

import numpy as np

from feyn.metrics.score import calculate_mi


class TestMI(unittest.TestCase):

    def setUp(self):
        self.X = np.array([4, 3, 1, 5])
        self.y = np.array(["a", "a", "b", "b"])

    def test_mutual_information(self):
        actual = 0.6931471805599452
        pred = calculate_mi([self.X], self.y)

        self.assertEqual(pred, actual)

    def test_mutual_information_cont(self):
        np.random.seed(42)
        X = np.random.random((1000,))
        Y = np.random.random((1000,))
        pred = calculate_mi([X], Y, float_bins=3)
        self.assertAlmostEqual(pred, 0, places=2)
   
    def testXOR(self):
        X = np.array([0, 0, 1, 1])
        Y = np.array([0, 1, 0, 1])
        Z = np.array([0, 1, 1, 0])
        actual = 0.6931471805599452
        assert (calculate_mi([X,Y], target = Z) == actual)
        