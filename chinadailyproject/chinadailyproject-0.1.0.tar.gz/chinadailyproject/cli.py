"""Console script for chinadailyproject."""
import argparse
import sys
from datetime import datetime

from chinadaily import download


def main():
    """Console script for chinadailyproject."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "chinadailyproject.cli.main")
    now = datetime.now()
    download(now)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
