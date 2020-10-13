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

        self.assertIsNone(parsed.date, "date is not None")

    def test_specified_date(self):
        date = "20201010"
        args = [date, ]
        parser = get_parser()
        parsed = parser.parse_args(args)

        self.assertEqual(parsed.date, datetime.strptime(date, CLI_DATE_FORMAT), f"parsed date is not match {date}")

    def test_wrong_date(self):
        date = "asdfasdf"
        args = [date, ]
        parser = get_parser()

        # todo(@yarving): catch errors
        parser.parse_args(args)
        self.fail(f"invalid date argument({date}) not catched")

    def test_extra_date_argument(self):
        """test more than 1 date passed in"""
        date = "20201010"
        args = [date, date]
        parser = get_parser()
        parsed = parser.parse_args(args)

        self.assertEqual(parsed.date, datetime.strptime(date, CLI_DATE_FORMAT), f"parsed date is not match {date}")
