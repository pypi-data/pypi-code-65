"""Console script for chinadaily."""
import argparse
import sys
from datetime import datetime

from chinadaily.chinadaily import download


def main():
    """Console script for chinadaily."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "chinadaily.cli.main")
    now = datetime.now()
    download(now)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
