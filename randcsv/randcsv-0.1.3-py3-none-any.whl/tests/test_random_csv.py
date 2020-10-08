import os
import unittest
from randcsv import RandCSV


class TestRandCSV(unittest.TestCase):

    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rand.csv")

    def setUp(self):
        try:
            os.remove(self.test_file)
        except OSError:
            pass

    def tearDown(self):
        try:
            os.remove(self.test_file)
        except OSError:
            pass

    def test_random_csv(self):
        csv = RandCSV(4, 3)
        csv.to_file('rand.csv')
        self.assertTrue(csv.rows, 4)
        self.assertTrue(csv.cols, 3)
        self.assertTrue(os.path.exists(self.test_file))

    def test_random_csv_with_title(self):
        csv = RandCSV(4, 3, title_row=True)
        csv.to_file('rand.csv')
        self.assertTrue(csv.rows, 4)
        self.assertTrue(csv.cols, 3)
        self.assertTrue(os.path.exists(self.test_file))

    def test_random_csv_with_index(self):
        csv = RandCSV(4, 3, index_col=True)
        csv.to_file('rand.csv')
        self.assertTrue(csv.rows, 4)
        self.assertTrue(csv.cols, 3)
        self.assertTrue(os.path.exists(self.test_file))

    def test_raises(self):
        with self.assertRaises(ValueError):
            RandCSV(4, 3, nan_freq=1.2)

        with self.assertRaises(ValueError):
            RandCSV(4, 3, empty_freq=1.2)

        with self.assertRaises(ValueError):
            RandCSV(4, 3, byte_size=-1)

        with self.assertRaises(ValueError):
            RandCSV(4, 3, nan_freq=0.4, empty_freq=0.7)
