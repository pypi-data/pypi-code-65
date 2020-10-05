#!/usr/bin/env python

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


"""Example fetcher converting some resources."""

import argparse
import asyncio
import shutil
from pathlib import Path
from typing import Iterator
from unittest import mock

from dbnomics_fetcher_toolbox.arguments import add_arguments_for_convert
from dbnomics_fetcher_toolbox.data_model import (
    DATASET_JSON,
    PROVIDER_JSON,
    write_series_jsonl,
)
from dbnomics_fetcher_toolbox.formats import write_json
from dbnomics_fetcher_toolbox.logging_utils import setup_logging
from dbnomics_fetcher_toolbox.resources import (
    DbnomicsDatasetResource,
    process_resources,
)
from dbnomics_fetcher_toolbox.status import load_events, open_status_writer

SCRIPT_DIR = Path(__file__).parent


async def main():
    """Entry point of the script."""
    parser = argparse.ArgumentParser()
    add_arguments_for_convert(parser)
    args = parser.parse_args()
    setup_logging(args)

    shutil.copyfile(src=SCRIPT_DIR / PROVIDER_JSON, dst=args.target_dir / PROVIDER_JSON)

    with mock.patch("pathlib.Path.glob") as mocked_glob:
        mocked_glob.return_value = list(map(Path, ["good.csv", "foobar.csv"]))
        resources = list(prepare_resources(args.source_dir, args.target_dir))
    events = load_events(args.target_dir)

    with open_status_writer(args) as append_event:
        await process_resources(
            resources=resources,
            args=args,
            process_resource=process_resource,
            on_event=append_event,
            events=events,
        )


class MyResource(DbnomicsDatasetResource):
    """A CSV resource for this dummy data provider."""

    source_csv_file: Path


def prepare_resources(source_dir: Path, target_dir: Path) -> Iterator[MyResource]:
    """Prepare resources to be processed."""
    for f in source_dir.glob("*.csv"):
        resource_id = f.stem
        yield MyResource(id=resource_id, source_csv_file=f, base_dir=target_dir)


def process_resource(resource: MyResource):
    """Generate a dataset following DBnomics data model."""

    # generate dataset.json
    dataset_json = {
        "code": resource.id,
    }
    write_json(resource.target_dir / DATASET_JSON, dataset_json)

    # Fail sample
    if resource.id == "foobar":
        raise ValueError("foobar is failing")

    # generate series.jsonl

    write_series_jsonl(
        resource.target_dir,
        [{"code": "A.FR.FOO"}, {"code": "M.FR.FOO"}, {"code": "Q.FR.FOO"}],
    )


if __name__ == "__main__":
    asyncio.run(main())
