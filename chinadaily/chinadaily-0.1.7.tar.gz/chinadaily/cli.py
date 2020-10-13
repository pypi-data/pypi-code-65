"""Console script for chinadaily."""
import argparse
import sys
from datetime import datetime

from .constants import CLI_DATE_FORMAT
from .chinadaily import download


def get_parser():
    """Ger argument parser"""
    parser = argparse.ArgumentParser("China Daily newspaper downloader")
    parser.add_argument('date', nargs='?',
                        type=lambda s: datetime.strptime(s, CLI_DATE_FORMAT),
                        help="specified date, default as today")

    return parser


def main():
    """Console script for chinadaily."""
    parser = get_parser()
    args = parser.parse_args()

    date = args.date if args.date else datetime.now()
    download(date)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
