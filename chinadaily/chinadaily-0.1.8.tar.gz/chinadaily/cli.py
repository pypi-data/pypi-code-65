"""Console script for chinadaily."""
import argparse
import sys
from datetime import datetime

from .constants import CLI_DATE_FORMAT
from .chinadaily import download


# todo(@yarving): auto generate version number
def get_version():
    """Get version number"""
    return '0.1.6'


def get_parser():
    """Get argument parser"""
    parser = argparse.ArgumentParser("China Daily newspaper downloader")
    parser.add_argument('date', nargs='*',
                        type=lambda s: datetime.strptime(s, CLI_DATE_FORMAT),
                        help="specified dates(default as today), multiple dates separated by blank")
    parser.add_argument('-v', '--version',
                        action='version', version=get_version(), help='Display version')

    return parser


def main():
    """Console script for chinadaily."""
    parser = get_parser()
    args = parser.parse_args()

    dates = args.date if args.date else [datetime.now()]
    for date in dates:
        download(date)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
