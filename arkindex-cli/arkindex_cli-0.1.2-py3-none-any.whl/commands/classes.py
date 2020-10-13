# -*- coding: utf-8 -*-
import argparse
import csv
from typing import Optional

import apistar
from rich import print
from rich.progress import Progress, track

from arkindex_cli.auth import Profiles


def add_classes_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "classes",
        help="Manage ML classes an Arkindex instance.",
        description="Manage ML classes an Arkindex instance.",
    )
    parser.add_argument(
        "csv_file",
        type=argparse.FileType("w", encoding="UTF-8"),
        help="Local CSV file to use",
    )
    parser.add_argument(
        "corpus_id",
        help="Manage ML classes of that Arkindex corpus",
        type=str,
    )
    parser.add_argument(
        "--init",
        default=False,
        action="store_true",
        help="Initialize a local CSV file with the classes of the corpus",
    )
    parser.set_defaults(func=run)


def run(
    corpus_id: str,
    csv_file,
    init: Optional[bool] = False,
    profile_slug: Optional[str] = None,
) -> int:

    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles()
        client = profiles.get_api_client_or_exit(profile_slug)

    # Load all ML classes in the corpus
    # They are immediately written to the file
    writer = csv.writer(csv_file)
    try:
        paginator = client.paginate("ListCorpusMLClasses", id=corpus_id)
        for cls in track(paginator, description="Loading ML Classes"):
            writer.writerow((cls["id"], cls["name"]))
    except apistar.exceptions.ErrorResponse as e:
        # Handle Api errors
        if e.status_code == 404:
            print(f"[yellow]:warning: The corpus {corpus_id} was not found")
        else:
            print(f"[red]An API error occurred: {e.content}")
