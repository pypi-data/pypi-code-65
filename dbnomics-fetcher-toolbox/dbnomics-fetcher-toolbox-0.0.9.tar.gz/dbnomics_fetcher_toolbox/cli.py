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

"""Functions for CLI commands."""

import argparse

from .arguments import readable_file
from .status import load_events_from_file


def status_stats():  # pragma: no cover
    """Compute and display statistics about a ``status.jsonl`` files."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "status_jsonl",
        type=readable_file,
        help="status.jsonl file containing events emitted during the process of "
        "resources",
    )
    parser.add_argument("--status", default=None, help="filter the resources by status")
    parser.add_argument("--type", default=None, help="filter the resources by type")
    args = parser.parse_args()

    events = load_events_from_file(args.status_jsonl)
    for event in events:
        if (args.status is None or event.status.value == args.status) and (
            args.type is None or event.type.value == args.type
        ):
            print(event.json())  # noqa: T001 CLI can print
