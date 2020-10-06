#! /usr/bin/env python3

# dbnomics-solr: Index DBnomics data into Apache Solr for full-text and faceted search.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2017-2020 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-solr
#
# dbnomics-solr is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-solr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Index DBnomics data into Apache Solr for full-text and faceted search."""


import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import List
from urllib.parse import quote

import daiquiri
import pysolr
import requests
import typer
from dbnomics_data_model import storages
from dbnomics_data_model.exceptions import StorageError
from dulwich.errors import NotGitRepository
from dulwich.repo import Repo
from environs import Env
from slugify import slugify
from solrq import Q
from toolz import count, get, get_in

INDEXATION = "INDEXATION"
DELETION = "DELETION"
GIT_MODE_TREE_STR = "040000"

DatasetCode = str


@dataclass
class AppArgs:
    """Represent script arguments common to all commands."""

    debug: bool = False


app = typer.Typer()
app_args = AppArgs()


logger = daiquiri.getLogger(__name__)

env = Env()
env.read_env()  # read .env file, if it exists


@app.callback()
def main(debug: bool = typer.Option(False, help="Display DEBUG log messages.")):
    """Index DBnomics data to Solr."""
    app_args.debug = debug


@app.command()
def index_providers():
    """Index many providers to Solr from STORAGE_DIR."""
    raise NotImplementedError()


@app.command()
def index_provider(
    storage_dir: Path,
    bare_repo_fallback: bool = typer.Option(
        env.bool("BARE_REPO_FALLBACK", False),
        help=(
            "If STORAGE_DIR does not exist, try opening the Git bare repository "
            'named "<STORAGE_DIR>.git".'
        ),
    ),
    full: bool = typer.Option(
        env.bool("FULL", False),
        help=(
            "Process all datasets. Default behavior is to process what changed "
            "since a previous commit."
        ),
    ),
    solr_url: str = typer.Option(
        env.str("SOLR_URL", default="http://localhost:8983/solr/dbnomics"),
        show_default=True,
    ),
    datasets: List[DatasetCode] = typer.Option(
        [], "--dataset", help="Index only the given datasets."
    ),
    excluded_datasets: List[DatasetCode] = typer.Option(
        [], "--exclude-dataset", help="Do not index the given datasets."
    ),
    start_from: DatasetCode = typer.Option(
        None, help="Start indexing from dataset code."
    ),
):
    """Index a single provider to Solr from STORAGE_DIR."""
    daiquiri.setup(level=logging.WARNING)
    logger.setLevel(logging.DEBUG if app_args.debug else logging.INFO)

    if solr_url.endswith("/"):
        solr_url = solr_url[:-1]

    if not storage_dir.is_dir() and bare_repo_fallback:
        bare_storage_dir = storage_dir.with_suffix(".git")
        if not storage_dir.is_dir() and bare_storage_dir.is_dir():
            logger.info(
                "Using Git bare repository from %r instead of %r that does not exist",
                str(bare_storage_dir),
                str(storage_dir),
            )
            storage_dir = bare_storage_dir

    if not storage_dir.is_dir():
        typer.echo(f"storage_dir {str(storage_dir)} not found")
        raise typer.Abort()

    storage = storages.init_storage(storage_dir)

    indexed_at = datetime.utcnow()
    logger.info("Using indexed_at %s for all documents", format_datetime(indexed_at))

    # Prepare a pysolr client for basic search and delete operations,
    # but not bulk indexing.

    solr = pysolr.Solr(solr_url)

    # Prepare provider

    provider_json = storage.load_provider_json()
    provider_code = provider_json["code"]
    logger.info("Provider code: %r", provider_code)

    try:
        repo = Repo(str(storage_dir))
    except NotGitRepository:
        repo = None

    current_provider_solr = get_provider(solr, provider_code)

    converted_at = None
    json_data_commit_ref = None

    created_at = None
    if current_provider_solr is not None:
        created_at = current_provider_solr.get("created_at")

    if repo is None:
        logger.info(
            "Storage directory is not a Git repository, provider and dataset "
            "Solr documents will not have %r properties",
            {"json_data_commit_ref", "converted_at", "created_at"},
        )
    elif b"HEAD" not in repo.get_refs():
        logger.info(
            "Storage directory is a Git repository but has no commit, provider "
            "and dataset Solr documents will not have %r properties",
            {"json_data_commit_ref", "converted_at", "created_at"},
        )
    else:
        json_data_commit_ref = repo.head().decode("utf-8")
        converted_at = (
            datetime.utcfromtimestamp(repo[repo.head()].author_time).isoformat() + "Z"
        )

        # Find and set `created_at` if not already filled.
        if created_at is None:
            git_log_reverse_cmd = 'git log --reverse --format="format:%at" | head -n1'
            logger.debug(
                "provider.created_at is unknown. Running command %r",
                git_log_reverse_cmd,
            )
            try:
                output = subprocess.check_output(  # noqa
                    git_log_reverse_cmd,
                    shell=True,
                    cwd=str(storage_dir),
                    universal_newlines=True,
                )
            except subprocess.CalledProcessError:
                logger.info(
                    "Could not read Git first commit date in %r (command: %r).",
                    str(storage_dir),
                    git_log_reverse_cmd,
                )
            else:
                commit_timestamp_str = output.strip()
                commit_datetime = datetime.utcfromtimestamp(int(commit_timestamp_str))
                created_at = commit_datetime.isoformat() + "Z"

    # Index datasets

    datasets_codes_actions = []

    if not full and current_provider_solr is None:
        logger.debug("Could not find provider document in Solr. Indexing all datasets.")
        full = True

    if not full:
        current_json_data_commit_ref = current_provider_solr.get("json_data_commit_ref")
        if current_json_data_commit_ref is None:
            logger.debug(
                "Could not read current JSON-data commit-ref from provider document "
                "in Solr. Indexing all datasets."
            )
            full = True

    if not full:
        # Ask Git which datasets directories were modified in latest commit
        # in json-data repository.
        git_diff_tree_cmd = "git diff-tree --no-commit-id --no-renames {}..".format(
            current_json_data_commit_ref
        )
        logger.info("Running command %r", git_diff_tree_cmd)
        try:
            output = subprocess.check_output(  # noqa
                git_diff_tree_cmd,
                shell=True,
                cwd=str(storage_dir),
                universal_newlines=True,
            )
        except subprocess.CalledProcessError:
            logger.info(
                "Could not compute Git diff-tree in %r (command: %r). "
                "Indexing all datasets.",
                str(storage_dir),
                git_diff_tree_cmd,
            )
            full = True
        else:
            output = output.strip()
            with StringIO(output) as fp:
                for line in fp:
                    old_mode, new_mode, _, _, action, entry_name = line.strip()[
                        1:
                    ].split()
                    if action in {"A", "M"} and new_mode == GIT_MODE_TREE_STR:
                        datasets_codes_actions.append((entry_name, INDEXATION))
                    elif action == "D" and old_mode == GIT_MODE_TREE_STR:
                        datasets_codes_actions.append((entry_name, DELETION))
                    else:
                        logger.error(
                            "Could not decide what to do with diff-tree line %r, "
                            "skipping line",
                            line,
                        )
                        continue

    if full:
        datasets_codes_actions = [
            (dataset_code, INDEXATION)
            for dataset_code in sorted(storage.iter_datasets_codes())
        ]

    logger.info("Mode: %s", "full" if full else "incremental")
    if not full:
        logger.info(
            "Datasets in Git diff-tree: %d modified, %d deleted",
            count(
                dataset_code
                for dataset_code, action in datasets_codes_actions
                if action == INDEXATION
            ),
            count(
                dataset_code
                for dataset_code, action in datasets_codes_actions
                if action == DELETION
            ),
        )

    # Apply script args: some datasets must be excluded.
    desired_datasets_codes_actions = [
        (dataset_code, action)
        for dataset_code, action in sorted(datasets_codes_actions)
        if is_desired_dataset(dataset_code, datasets, excluded_datasets, start_from)
    ]
    if not desired_datasets_codes_actions:
        logger.info("No datasets to process, skipping provider processing too")
    else:
        logger.info("Processing %d datasets...", len(desired_datasets_codes_actions))
        dataset_solr_iter = (
            json.dumps(dataset_solr, ensure_ascii=False).encode("utf-8")
            for dataset_solr in iter_dataset_solr(
                solr,
                repo,
                storage,
                provider_json,
                indexed_at,
                desired_datasets_codes_actions,
            )
        )
        # Bulk indexing from generated JSON lines.
        # pysolr doesn't support this so let's call directly a specific endpoint.
        # Cf https://lucene.apache.org/solr/guide/6_6/transforming-and-indexing-custom-json.html#TransformingandIndexingCustomJSON-MultipledocumentsinaSinglePayload # noqa
        # Cf https://requests.readthedocs.io/en/master/user/advanced/#chunk-encoded-requests # noqa
        response = requests.post(
            "{}/update/json/docs?commit=true".format(solr_url), data=dataset_solr_iter
        )
        response.raise_for_status()

        logger.info("Processing provider...")
        provider_solr = {
            "id": provider_code,
            "created_at": created_at,
            "converted_at": converted_at,
            "indexed_at": format_datetime(indexed_at),
            "json_data_commit_ref": json_data_commit_ref,
            "type": "provider",
            "code": provider_code,
            "slug": slugify(provider_code),
            "name": provider_json.get("name"),
            "region": provider_json.get("region"),
            "terms_of_use": provider_json.get("terms_of_use"),
            "website": provider_json.get("website"),
        }
        solr.add(docs=[without_none_values(provider_solr)])

    delete_obsolete_documents(
        solr,
        desired_datasets_codes_actions,
        provider_code,
        indexed_at,
        full,
        datasets,
        excluded_datasets,
    )

    logger.info("Committing Solr changes...")
    solr.commit()


def format_datetime(d):
    """Format datetime with timezone."""
    return d.isoformat() + "Z"


def str_datetime_to_solr(s):
    """Normalize datetime for Solr.

    >>> str_datetime_to_solr('2017-07-06')
    '2017-07-06T00:00:00Z'
    >>> str_datetime_to_solr('2016-01-04T10:35:59-05:00')
    '2016-01-04T15:35:59Z'
    >>> str_datetime_to_solr('2016-01-04T15:35:59Z')
    '2016-01-04T15:35:59Z'
    """
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    d = datetime.fromisoformat(s)
    if d.tzinfo:
        d = d.astimezone(timezone.utc).replace(tzinfo=None)
    return d.isoformat() + "Z"


def build_dataset_solr(solr, provider_json, dataset_json, indexed_at, repo):
    """Build a JSON object for a dataset, following the Solr schema."""
    provider_code = provider_json["code"]
    dataset_code = dataset_json["code"]

    updated_at = dataset_json.get("updated_at")
    if updated_at:
        updated_at = str_datetime_to_solr(updated_at)

    dataset_solr = {
        "id": "{}/{}".format(provider_json["code"], dataset_json["code"]),
        "indexed_at": format_datetime(indexed_at),
        "type": "dataset",
        "code": dataset_code,
        "provider_code": provider_code,
        "provider_name": provider_json.get("name"),
        "name": dataset_json.get("name"),
        "description": dataset_json.get("description"),
        "updated_at": updated_at,
        "nb_series": 0,  # Will be incremented if dataset has series.
    }

    if repo is not None and b"HEAD" in repo.get_refs():
        # Find and set `converted_at` and `json_data_commit_ref`
        # according to latest commit in json-data repo.
        output = subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%H %at", "--", dataset_json["code"]],
            cwd=repo.path,
        ).decode("utf-8")
        output = output.strip()
        if output:
            # `output` can be empty if specific dataset directory
            # is not committed in Git.
            commit_ref, commit_timestamp_str = output.split(" ", 1)
            commit_datetime = datetime.utcfromtimestamp(int(commit_timestamp_str))
            dataset_solr["converted_at"] = commit_datetime.isoformat() + "Z"
            dataset_solr["json_data_commit_ref"] = commit_ref

        # Find and set `created_at` if not already filled,
        # according to oldest commit in json-data repo.
        current_dataset_solr = get_dataset(solr, provider_code, dataset_code)
        created_at = None
        if current_dataset_solr is not None:
            created_at = current_dataset_solr.get("created_at")
        if created_at is None:
            git_log_reverse_cmd = (
                'git log --reverse --format="format:%at" -- {} | '
                "head -n1".format(dataset_code)
            )
            logger.debug(
                "dataset.created_at is unknown. Running command %r", git_log_reverse_cmd
            )
            try:
                output = subprocess.check_output(  # noqa
                    git_log_reverse_cmd,
                    shell=True,
                    cwd=repo.path,
                    universal_newlines=True,
                )
            except subprocess.CalledProcessError:
                logger.info(
                    "Could not read Git first commit date in %r (command: %r).",
                    repo.path,
                    git_log_reverse_cmd,
                )
            else:
                commit_timestamp_str = output.strip()
                if commit_timestamp_str:
                    commit_datetime = datetime.utcfromtimestamp(
                        int(commit_timestamp_str)
                    )
                    dataset_solr["created_at"] = commit_datetime.isoformat() + "Z"

    return dataset_solr


def build_series_solr(
    provider_json, dataset_json, series_json, indexed_at, series_jsonl_offset=None
):
    """Build a JSON object for a series, following the Solr schema."""
    provider_code = provider_json["code"]
    dataset_code = dataset_json["code"]
    series_code = series_json["code"]
    series_solr = {
        "id": "{}/{}/{}".format(provider_code, dataset_code, series_code),
        "indexed_at": format_datetime(indexed_at),
        "type": "series",
        "code": series_json["code"],
        "name": series_json.get("name"),
        "provider_code": provider_code,
        "provider_name": provider_json.get("name"),
        "dataset_id": "{}/{}".format(provider_code, dataset_code),
        "dataset_code": dataset_code,
        "dataset_name": dataset_json.get("name"),
    }
    dimensions = series_json.get("dimensions", {})
    if isinstance(dimensions, list):
        dimensions_codes_order = dataset_json["dimensions_codes_order"]
        assert len(dimensions) == len(dimensions_codes_order), (
            dimensions_codes_order,
            dimensions,
        )
        dimensions = dict(zip(dimensions_codes_order, dimensions))
    for dimension_code, dimension_value_code in dimensions.items():
        # Index dimensions codes to compute facets.
        series_solr[
            "dimension_value_code.{}".format(quote(dimension_code))
        ] = dimension_value_code

    def iter_dimensions_values_labels():
        for dimension_code, dimension_value_code in dimensions.items():
            dimension_value_label = get_in(
                ["dimensions_values_labels", dimension_code, dimension_value_code],
                dataset_json,
                default=None,
            )
            if dimension_value_label is not None:
                yield dimension_value_label

    dimensions_values_labels = list(iter_dimensions_values_labels())
    if dimensions_values_labels:
        series_solr["dimensions_values_labels"] = dimensions_values_labels

    if series_jsonl_offset is not None:
        series_solr["series_jsonl_offset"] = series_jsonl_offset

    return series_solr


def delete_obsolete_documents(
    solr,
    desired_datasets_codes_actions,
    provider_code,
    indexed_at,
    full,
    datasets,
    excluded_datasets,
):
    """Delete obsolete documents from Solr index."""
    # Delete datasets marked for deletion.
    datasets_codes_to_delete = sorted(
        dataset_code
        for dataset_code, action in desired_datasets_codes_actions
        if action == DELETION
    )
    if datasets_codes_to_delete:
        logger.info(
            "Incremental mode: deleting datasets marked for deletion (%r)...",
            datasets_codes_to_delete,
        )
        provider_criteria = Q(provider_code=provider_code)

        for dataset_code in datasets_codes_to_delete:
            dataset_criteria = Q(type="dataset", code=dataset_code) | Q(
                type="series", dataset_code=dataset_code
            )
            solr.delete(q=provider_criteria & dataset_criteria, commit=False)

    # Delete obsolete series of indexed datasets with different than indexed_at.
    indexed_datasets_codes = sorted(
        dataset_code
        for dataset_code, action in desired_datasets_codes_actions
        if action == INDEXATION
    )
    if indexed_datasets_codes:
        for dataset_code in indexed_datasets_codes:
            # Hack: build Solr query half with solrq, half manually, because I could not
            # achieve working with parentheses generated by solrq when doing
            # Q(...) & ~Q(...) => (...) AND (!...)
            # Solr did not work with the "!" inside parentheses.
            obsolete_docs_query1 = Q(
                type="series", provider_code=provider_code, dataset_code=dataset_code
            )
            obsolete_docs_query2 = Q(indexed_at=indexed_at)
            obsolete_docs_query = (
                f"{obsolete_docs_query1} AND NOT {obsolete_docs_query2}"
            )
            nb_obsolete_docs = solr.search(q=obsolete_docs_query).hits
            if nb_obsolete_docs > 0:
                logger.info(
                    "Deleting %d series belonging to dataset %r, "
                    "different than indexed_at (%s)...",
                    nb_obsolete_docs,
                    dataset_code,
                    format_datetime(indexed_at),
                )
                solr.delete(q=obsolete_docs_query, commit=False)

    # Delete obsolete datasets (and their series) different than indexed_at.
    if full and not datasets and not excluded_datasets:
        # Hack: see above.
        type_criteria = Q(type="dataset") | Q(type="series")
        obsolete_docs_query1 = type_criteria & Q(provider_code=provider_code)
        obsolete_docs_query2 = Q(indexed_at=indexed_at)
        obsolete_docs_query = f"{obsolete_docs_query1} AND NOT {obsolete_docs_query2}"
        nb_obsolete_docs = solr.search(q=obsolete_docs_query).hits
        if nb_obsolete_docs > 0:
            logger.info(
                "Full mode: deleting %d documents (datasets and series) "
                "different than indexed_at (%s)...",
                nb_obsolete_docs,
                format_datetime(indexed_at),
            )
            solr.delete(q=obsolete_docs_query, commit=False)


def is_desired_dataset(dataset_code, datasets, excluded_datasets, start_from):
    """Apply script arguments to detemine if a dataset has to be indexed."""
    if datasets and dataset_code not in datasets:
        logger.debug(
            "Skipping dataset %r because it is not mentioned by --datasets option",
            dataset_code,
        )
        return False
    if excluded_datasets and dataset_code in excluded_datasets:
        logger.debug(
            "Skipping dataset %r because it is mentioned by --exclude-datasets option",
            dataset_code,
        )
        return False
    if start_from is not None and dataset_code < start_from:
        logger.debug("Skipping dataset %r because of --start-from option", dataset_code)
        return False
    return True


def iter_dataset_solr(
    solr,
    repo,
    storage,
    provider_json,
    indexed_at,
    desired_datasets_codes_actions,
):
    """Yield dataset dicts as required by Solr."""
    # Iterate over datasets and index or delete each of them.
    for dataset_index, (dataset_code, action) in enumerate(
        desired_datasets_codes_actions, start=1
    ):
        if action == INDEXATION:
            logger.info(
                "Indexing dataset %r (%d/%d)",
                dataset_code,
                dataset_index,
                len(desired_datasets_codes_actions),
            )

            dataset_dir = storage.load_dataset_dir(dataset_code)

            try:
                dataset_json = dataset_dir.load_dataset_json()
            except StorageError:
                logger.exception(
                    "Could not load `dataset.json` for dataset %r", dataset_code
                )
                continue

            dataset_solr = build_dataset_solr(
                solr, provider_json, dataset_json, indexed_at, repo
            )
            dataset_series = dataset_json.get("series")

            for series_index, (series_json, metadata) in enumerate(
                dataset_dir.iter_series_json(
                    add_metadata=True, dataset_series=dataset_series
                ),
                start=1,
            ):
                if series_index > 0 and series_index % 1000 == 0:
                    logger.debug("Indexed %d series so far...", series_index)
                series_jsonl_offset = metadata.get("series_jsonl_offset")
                series_solr = build_series_solr(
                    provider_json,
                    dataset_json,
                    series_json,
                    indexed_at,
                    series_jsonl_offset,
                )
                yield series_solr
                dataset_solr["nb_series"] += 1

            logger.info("Indexed %d series total", dataset_solr["nb_series"])

            yield dataset_solr

            # Obsolete series of the current dataset will be removed later.

        elif action == DELETION:
            # To avoid overlapping commits, mark datasets to delete then
            # delete them later.
            logger.info(
                "Marking dataset %r for (future) deletion (%d/%d)",
                dataset_code,
                dataset_index,
                len(desired_datasets_codes_actions),
            )

        else:
            raise ValueError("Unexpected action: {!r}".format(action))


def get_dataset(solr, provider_code, dataset_code):
    """Find a dataset by code in Solr."""
    results = solr.search(
        q=Q(type="dataset", provider_code=provider_code, code=dataset_code),
        rows=1,
    )
    return get(0, results.docs, default=None)


def get_provider(solr, provider_code):
    """Find a provider by code in Solr."""
    results = solr.search(q=Q(type="provider", code=provider_code), rows=1)
    return get(0, results.docs, default=None)


def without_none_values(d):
    """Return a copy of d without None values."""
    return {k: v for k, v in d.items() if v is not None}


if __name__ == "__main__":
    app()
