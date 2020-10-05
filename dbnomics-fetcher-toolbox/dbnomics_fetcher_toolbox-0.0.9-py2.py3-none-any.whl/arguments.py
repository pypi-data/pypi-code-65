# dbnomics-fetcher-toolbox
# Toolbox of functions and data types helping writing DBnomics fetchers.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2019 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-fetcher-toolbox
#
# dbnomics-fetcher-toolbox is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-fetcher-toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Functions handling script options of fetchers."""

import argparse
import os
import platform
from pathlib import Path

from .status import STATUS_JSONL


def add_arguments_for_download(parser: argparse.ArgumentParser):
    """Add arguments to ``parser`` used for a download script."""
    parser.add_argument(
        "target_dir", type=readable_dir, help="directory where provider data is written"
    )
    add_common_arguments(parser)


def add_arguments_for_convert(parser: argparse.ArgumentParser):
    """Add arguments to ``parser`` used for a convert script."""
    parser.add_argument(
        "source_dir", type=readable_dir, help="directory containing provider data"
    )
    parser.add_argument(
        "target_dir",
        type=readable_dir,
        help="directory where converted data is written",
    )
    add_common_arguments(parser)


def add_common_arguments(parser: argparse.ArgumentParser):
    """Add common arguments to ``parser``.

    Those arguments are common to both download and convert scripts.
    """
    if platform.python_version_tuple() < ("3", "8"):

        class ExtendAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                items = getattr(namespace, self.dest) or []
                items.extend(values)
                setattr(namespace, self.dest, items)

        parser.register("action", "extend", ExtendAction)

    parser.add_argument(
        "--debug", action="store_true", help="display script DEBUG logs"
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="process all resources, even if already processed",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="process resources that failed previously",
    )
    parser.add_argument(
        "--only",
        action="extend",
        nargs="+",
        help="process only the specified resources",
    )
    parser.add_argument(
        "--exclude",
        action="extend",
        nargs="+",
        help="do not process the specified resources",
    )
    parser.add_argument(
        "--limit",
        type=natural_int,
        help="process a maximum number of resources",
    )
    parser.add_argument(
        "--delete-on-error",
        action="store_true",
        help="delete resource when an error occurred during its processing",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="exit instantly on first exception instead of logging it "
        "(useful to launch the script with a debugger like pdb or ipdb)"
        "and processing next resource",
    )
    parser.add_argument(
        "--flush-status",
        action="store_true",
        help=f"flush the {STATUS_JSONL} file after each write",
    )


def natural_int(value: str) -> int:
    """Check that ``value`` is a positive integer."""
    try:
        int_value = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer number") from exc
    if int_value < 0:
        raise argparse.ArgumentTypeError(f"{value!r} is not a positive number")
    return int_value


def readable_dir(value: str) -> Path:
    """Check that ``value`` is a readable directory.

    Example::

        parser.add_argument('dir', type=readable_dir)
    """
    path = Path(value)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{value!r} is not a directory")
    if not os.access(value, os.R_OK):
        raise argparse.ArgumentTypeError(f"{value!r} directory is not readable")
    return path


def readable_file(value: str) -> Path:
    """Check that ``value`` is a readable file.

    Example::

        parser.add_argument('file', type=readable_file)
    """
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"{value!r} is not a file")
    if not os.access(value, os.R_OK):
        raise argparse.ArgumentTypeError(f"{value!r} file is not readable")
    return path
