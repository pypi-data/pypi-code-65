import os
import unittest
from randcsv.cli import parse_args, cli


class TestCLI(unittest.TestCase):

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

    def test_parse_args(self):
        args = parse_args(["-m", "4", "-n", "3", "-d", "float"])
        self.assertEqual(args.rows, 4)
        self.assertEqual(args.cols, 3)
        self.assertEqual(args.data_types, ["float"])

        args = parse_args(["-m", "4", "-n", "3"])
        self.assertEqual(args.rows, 4)
        self.assertEqual(args.cols, 3)
        self.assertEqual(args.data_types, ["integer"])

    def test_cli(self):
        cli(["-m", "4", "-n", "3"])
        self.assertTrue(os.path.exists(self.test_file))
