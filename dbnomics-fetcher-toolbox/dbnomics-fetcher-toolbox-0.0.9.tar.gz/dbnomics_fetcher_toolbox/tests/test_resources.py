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

"""Tests about ``resources`` module."""

import argparse
from pathlib import Path

import pytest

from dbnomics_fetcher_toolbox.arguments import add_arguments_for_download
from dbnomics_fetcher_toolbox.resources import (
    Resource,
    _should_process_resource,
    process_resources,
)
from dbnomics_fetcher_toolbox.status import (
    ResourceEvent,
    ResourceStatus,
    load_events,
    open_status_writer,
)


def default_process_resource(resource: Resource):
    """Act as a `process_resource` function that does nothing."""
    pass


def prepare_args(target_dir: Path, args_str: str = None):
    """Prepare command-line args for test cases."""
    if args_str is None:
        args_str = ""

    parser = argparse.ArgumentParser()
    add_arguments_for_download(parser)
    additional_arg_list = filter(None, args_str.split(" "))
    return parser.parse_args(args=[str(target_dir), *additional_arg_list])


@pytest.mark.asyncio
async def test_process_all_resources(tmp_path):
    """Process all resources."""
    events = load_events(tmp_path)
    assert events is None

    resources = [Resource(id=letter) for letter in list("ABCDEF")]
    args = prepare_args(tmp_path)

    with open_status_writer(args) as append_event:
        resource_event_by_id = await process_resources(
            resources=resources,
            args=args,
            process_resource=default_process_resource,
            on_event=append_event,
            events=events,
        )

    assert resource_event_by_id is not None
    assert len(resource_event_by_id) == len(resources)
    assert all(
        evt.status == ResourceStatus.SUCCESS for evt in resource_event_by_id.values()
    )


@pytest.mark.asyncio
async def test_process_one_resource(tmp_path):
    """Process ony one resource."""
    events = load_events(tmp_path)
    assert events is None

    resources = [Resource(id=letter) for letter in list("ABCDEF")]
    selected_resource_id = "C"
    args = prepare_args(tmp_path, f"--only {selected_resource_id}")

    with open_status_writer(args) as append_event:
        resource_event_by_id = await process_resources(
            resources=resources,
            args=args,
            process_resource=default_process_resource,
            on_event=append_event,
            events=events,
        )

    assert resource_event_by_id is not None
    assert len(resource_event_by_id) == len(resources)
    assert all(
        evt.status == ResourceStatus.SKIPPED
        for resource_id, evt in resource_event_by_id.items()
        if resource_id != selected_resource_id
    )
    assert resource_event_by_id[selected_resource_id].status == ResourceStatus.SUCCESS


@pytest.mark.asyncio
async def test_exclude_some_resources(tmp_path):
    """Process all resources except some ones."""
    events = load_events(tmp_path)
    assert events is None

    resources = [Resource(id=letter) for letter in list("ABCDEF")]
    excluded_resources_str = "A E"
    excluded_resource_id_list = excluded_resources_str.split(" ")
    args = prepare_args(tmp_path, f"--exclude {excluded_resources_str}")

    with open_status_writer(args) as append_event:
        resource_event_by_id = await process_resources(
            resources=resources,
            args=args,
            process_resource=default_process_resource,
            on_event=append_event,
            events=events,
        )

    assert resource_event_by_id is not None
    assert len(resource_event_by_id) == len(resources)
    assert all(
        evt.status == ResourceStatus.SKIPPED
        for resource_id, evt in resource_event_by_id.items()
        if resource_id in excluded_resource_id_list
    )
    assert all(
        evt.status == ResourceStatus.SUCCESS
        for resource_id, evt in resource_event_by_id.items()
        if resource_id not in excluded_resource_id_list
    )


@pytest.mark.asyncio
async def test_limit_processed_resources(tmp_path):
    """Process a limited number of resources."""
    events = load_events(tmp_path)
    assert events is None

    resources = [Resource(id=letter) for letter in list("ABCDEF")]
    limit_count = 4
    processed_resource_id_list = [resource.id for resource in resources[:limit_count]]
    args = prepare_args(tmp_path, f"--limit {limit_count}")

    with open_status_writer(args) as append_event:
        resource_event_by_id = await process_resources(
            resources=resources,
            args=args,
            process_resource=default_process_resource,
            on_event=append_event,
            events=events,
        )

    assert resource_event_by_id is not None
    assert len(resource_event_by_id) == len(resources)
    assert all(
        evt.status == ResourceStatus.SUCCESS
        for resource_id, evt in resource_event_by_id.items()
        if resource_id in processed_resource_id_list
    )
    assert all(
        evt.status == ResourceStatus.SKIPPED
        for resource_id, evt in resource_event_by_id.items()
        if resource_id not in processed_resource_id_list
    )


def test_should_process_resource_no_event(tmp_path):
    """Should process if resource has not been processed yet."""
    args = prepare_args(tmp_path)
    assert _should_process_resource(args)


def test_should_process_resource_success(tmp_path):
    """Should not process if resource has already been successfully processed."""
    args = prepare_args(tmp_path)
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.SUCCESS)
    assert not _should_process_resource(args, event=event)


def test_should_process_resource_success_force(tmp_path):
    """Should process successfully previously processed resource if --force is set."""
    args = prepare_args(tmp_path, "--force")
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.SUCCESS)
    assert _should_process_resource(args, event=event)


def test_should_process_resource_success_retry_failed(tmp_path):
    """Should not process succesfully previously resource if --retry-failed is set."""
    args = prepare_args(tmp_path, "--retry-failed")
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.SUCCESS)
    assert not _should_process_resource(args, event=event)


def test_should_process_resource_failure(tmp_path):
    """Should not process if last resource process failed."""
    args = prepare_args(tmp_path)
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.FAILURE)
    assert not _should_process_resource(args, event=event)


def test_should_process_resource_failure_force(tmp_path):
    """Should process failure previously processed resource if --force is set."""
    args = prepare_args(tmp_path, "--force")
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.FAILURE)
    assert _should_process_resource(args, event=event)


def test_should_process_resource_failure_retry_failed(tmp_path):
    """Should process previously failed resource if --retry-failed is set."""
    args = prepare_args(tmp_path, "--retry-failed")
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.FAILURE)
    assert _should_process_resource(args, event=event)


def test_should_process_resource_skipped(tmp_path):
    """Should process if last resource process was skipped."""
    args = prepare_args(tmp_path)
    event = ResourceEvent(id="A", duration=1, status=ResourceStatus.SKIPPED)
    assert _should_process_resource(args, event=event)
