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


"""Example fetcher downloading some resources."""

import argparse
import asyncio
from pathlib import Path
from typing import Iterator

from dbnomics_fetcher_toolbox.arguments import add_arguments_for_download
from dbnomics_fetcher_toolbox.logging_utils import setup_logging
from dbnomics_fetcher_toolbox.resources import Resource, process_resources
from dbnomics_fetcher_toolbox.status import load_events, open_status_writer


async def main():
    """Entry point of the script."""
    parser = argparse.ArgumentParser()
    add_arguments_for_download(parser)
    args = parser.parse_args()
    setup_logging(args)

    resources = list(prepare_resources(args.target_dir))
    events = load_events(args.target_dir)

    with open_status_writer(args) as append_event:
        await process_resources(
            resources=resources,
            args=args,
            process_resource=process_resource,
            on_event=append_event,
            events=events,
        )


class MyResource(Resource):
    """A resource for this dummy data provider."""

    file: Path
    url: str

    def delete(self):
        """Delete the resource file."""
        self.file.unlink()


def prepare_resources(target_dir: Path) -> Iterator[MyResource]:
    """Prepare resources to be processed."""
    for i in range(3):
        resource_id = f"DATASET{i}"
        yield MyResource(
            id=resource_id,
            url=f"https://stats.provider.com/datasets/{i}.xls",
            file=(target_dir / resource_id).with_suffix(".txt"),
        )


def process_resource(resource: MyResource):
    """Process a single resource."""
    if resource.id == "DATASET2":
        raise ValueError("oh no!")
    resource.file.write_text(resource.url)


if __name__ == "__main__":
    asyncio.run(main())
