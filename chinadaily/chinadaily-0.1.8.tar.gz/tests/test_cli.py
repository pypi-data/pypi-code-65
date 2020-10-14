from argparse import ArgumentError
from datetime import datetime
from unittest import TestCase

from chinadaily.cli import get_parser
from chinadaily.constants import CLI_DATE_FORMAT


class TestParser(TestCase):

    def test_date_not_given(self):

        # test positional parameter as:
        # - default
        # - specified date

        # test date range
        args = []
        parser = get_parser()
        parsed = parser.parse_args(args)

        self.assertEqual(len(parsed.date), 0, "date argument is not empty")
        self.assertListEqual(parsed.date, [], "date is not None")

    def test_specified_date(self):
        date = "20201010"
        args = [date, ]
        parser = get_parser()
        parsed = parser.parse_args(args)

        self.assertEqual(len(parsed.date), 1, "date argument is not one")
        self.assertEqual(parsed.date,
                         [datetime.strptime(date, CLI_DATE_FORMAT)],
                         f"parsed date is not match {date}")

    def test_wrong_date(self):
        date = "asdfasdf"
        args = [date, ]
        parser = get_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(args)

    def test_multiple_date_argument(self):
        """test more than 1 date passed in"""
        date1 = "20201010"
        date2 = "20201011"
        args = [date1, date2]
        parser = get_parser()
        parsed = parser.parse_args(args)

        self.assertEqual(len(parsed.date), 2, "date argument count is not 2")
        self.assertEqual(parsed.date,
                         [datetime.strptime(date1, CLI_DATE_FORMAT), datetime.strptime(date2, CLI_DATE_FORMAT)],
                         f"parsed date is not match")
