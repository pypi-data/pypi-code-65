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


"""Functions and data types helping processing resources in DBnomics fetchers."""


import argparse
import asyncio
import shutil
from pathlib import Path
from typing import Awaitable, Callable, Dict, Sequence, Set

import daiquiri
from contexttimer import Timer
from humanfriendly import format_number, format_timespan, pluralize
from pydantic import BaseModel
from toolz import take

from .status import EventType, ResourceEvent, ResourceStatus

logger = daiquiri.getLogger(__name__)

ResourceId = str


class Resource(BaseModel):
    """A resource to be processed by :func:`process_resources`."""

    id: ResourceId  # noqa

    def create_context(self):
        """Create a context necessary to process the resource.

        This method is called by :func:`process_resources` before calling
        ``process_resource``.

        Override it to do anything you need (e.g. creating a directory...).
        """

    def delete(self):
        """Delete a resource.

        This method is called by :func:`process_resources` if any error occurred
        during the execution of the ``process_resource`` callback.

        Override it to do anything you need (e.g. delete a directory...).
        """


class DbnomicsDatasetResource(Resource):
    """A resource representing a dataset converted to DBnomics data model."""

    base_dir: Path

    @property
    def target_dir(self) -> Path:
        """Directory where the dataset will be written, following DBnomics data model.

        The name of the directory is the resource ``id``.
        """
        return self.base_dir / self.id

    def create_context(self):
        """Create the dataset target directory, following DBnomics data model."""
        self.target_dir.mkdir(exist_ok=True)

    def delete(self):
        """Delete the dataset target directory, following DBnomics data model."""
        shutil.rmtree(self.target_dir)


ProcessResourceCallback = Callable[[Resource], Awaitable[None]]
OnEventCallback = Callable[[ResourceEvent], None]


async def process_resources(
    resources: Sequence[Resource],
    args: argparse.Namespace,
    process_resource: ProcessResourceCallback,
    on_event: OnEventCallback = None,
    events: Sequence[ResourceEvent] = None,
) -> Dict[ResourceId, ResourceEvent]:
    """Handle the common work of processing resources.

    Iterate over ``resources``:

    * removing the excluded ones if the ``--exclude`` option is used
    * keeping only some of them if the ``--only`` option is used
    * processing a limited number of resources if the ``--limit`` option is used

    By default do not process resources that were already processed with
    ``SUCCESS`` or ``FAILURE`` status.
    If the option ``--retry-failed`` is used, retry resources with FAILURE status.
    If the option ``--force`` is used, process all resources.

    For each resource, call ``process_resource(resource)``, logging messages allowing
    to track the processing progress.
    If an exception is raised during the execution of ``process_resource``:

    * log the error and process the next resource,
      or re-raise if ``--fail-fast`` option is used
    * call ``resource.delete()`` if ``--delete-on-error`` option is used
    """
    if events is None:
        events = []

    resource_event_by_id = {
        event.id: event for event in events if event.type == EventType.RESOURCE
    }

    resources_to_process = _filter_resources_with_args(
        resources,
        args,
        resource_event_by_id,
        on_event=on_event,
    )

    if not resources_to_process:
        logger.debug(
            "No resource to process was found among %s",
            pluralize(len(resources), "resource"),
        )
        return resource_event_by_id

    ids = ", ".join(resource.id for resource in resources_to_process)
    logger.debug(
        "About to process %s: %s",
        pluralize(len(resources_to_process), "resource"),
        ids,
    )

    await _process_resources_in_sequence(
        args=args,
        process_resource=process_resource,
        resources_to_process=resources_to_process,
        resource_event_by_id=resource_event_by_id,
        on_event=on_event,
    )

    return resource_event_by_id


async def _process_resources_in_sequence(
    args: argparse.Namespace,
    process_resource: ProcessResourceCallback,
    resources_to_process: Sequence[Resource],
    resource_event_by_id: Dict[ResourceId, ResourceEvent],
    on_event: OnEventCallback = None,
):
    for resource_number, resource in enumerate(resources_to_process, start=1):
        await _process_resource_wrapper(
            args=args,
            process_resource=process_resource,
            resources_to_process=resources_to_process,
            resource_event_by_id=resource_event_by_id,
            resource=resource,
            resource_number=resource_number,
            on_event=on_event,
        )


async def _process_resource_wrapper(
    args: argparse.Namespace,
    process_resource: ProcessResourceCallback,
    resources_to_process: Sequence[Resource],
    resource_event_by_id: Dict[ResourceId, ResourceEvent],
    resource: Resource,
    resource_number: int,
    on_event: OnEventCallback = None,
):
    event = resource_event_by_id.get(resource.id)
    if not _should_process_resource(args, event=event):
        assert event is not None, event
        logger.debug(
            "Do not process resource %d/%d because it was already processed (%s)",
            resource_number,
            len(resources_to_process),
            event.status.value,
            resource=resource.id,
        )
        return

    logger.info(
        "Processing resource %d/%d",
        resource_number,
        len(resources_to_process),
        resource=resource.id,
    )

    with Timer() as t:
        resource.create_context()
        try:
            if asyncio.iscoroutinefunction(process_resource):
                await process_resource(resource)
            else:
                process_resource(resource)
        except Exception as exc:
            event = ResourceEvent(
                id=resource.id,
                status=ResourceStatus.FAILURE,
                duration=t.elapsed,
                message=str(exc),
            )
            resource_event_by_id[resource.id] = event
            if on_event:
                on_event(event)
            if args.delete_on_error:
                logger.debug("Deleting resource data", resource=resource.id)
                resource.delete()
            logger.error(  # noqa
                "Error processing resource after %s",
                format_timespan(t.elapsed),
                resource=resource.id,
                exc_info=not args.fail_fast,
            )
            if args.fail_fast:
                raise
        else:
            event = ResourceEvent(
                id=resource.id,
                status=ResourceStatus.SUCCESS,
                duration=t.elapsed,
            )
            resource_event_by_id[resource.id] = event
            if on_event:
                on_event(event)
            logger.info(
                "Resource processed in %s",
                format_timespan(t.elapsed),
                resource=resource.id,
            )


def _should_process_resource(args: argparse.Namespace, event: ResourceEvent = None):
    return (
        args.force
        or event is None
        or (
            event.status != ResourceStatus.SUCCESS
            and (event.status != ResourceStatus.FAILURE or args.retry_failed)
        )
    )


def _filter_resources_with_args(
    resources: Sequence[Resource],
    args: argparse.Namespace,
    resource_event_by_id: Dict[ResourceId, ResourceEvent],
    on_event: OnEventCallback = None,
) -> Sequence[Resource]:
    """Filter ``resources`` by applying ``args``, and update ``resource_event_by_id``.

    Script optiona taken into account: ``--only``, ``--exclude`` and ``--limit``.

    For every resource filtered-out by script options, add a
    :class:`dbnomics_fetcher_toolbox.status.ResourceEvent` to ``resource_event_by_id``.
    """
    all_resource_ids = {r.id for r in resources}

    # Initialize `resources_to_process` with all `resources`.
    # The script options will be applied below, restricting this list.
    resources_to_process = resources

    if args.only:
        option_name = "--only"
        valid_only = _validate_resources(all_resource_ids, set(args.only), option_name)
        logger.debug(
            "Process only %d of %s because of %s: %s",
            len(valid_only),
            pluralize(len(resources), "resource"),
            option_name,
            ", ".join(valid_only),
        )
        resources_to_process = [
            resource for resource in resources_to_process if resource.id in valid_only
        ]
        _add_skipped_events(
            resources,
            resources_to_process,
            resource_event_by_id,
            option_name,
            on_event=on_event,
        )

    if args.exclude:
        option_name = "--exclude"
        valid_exclude = _validate_resources(
            all_resource_ids, set(args.exclude), option_name
        )
        logger.debug(
            "Exclude %d of %s because of %s: %s",
            len(valid_exclude),
            pluralize(len(resources), "resource"),
            option_name,
            ", ".join(valid_exclude),
        )
        resources_to_process = [
            resource
            for resource in resources_to_process
            if resource.id not in valid_exclude
        ]
        _add_skipped_events(
            resources,
            resources_to_process,
            resource_event_by_id,
            option_name,
            on_event=on_event,
        )

    if args.limit is not None:
        option_name = "--limit"
        logger.debug(
            "%s because of %s",
            "Process only the first resource"
            if args.limit == 1
            else "Don't process any resource"
            if args.limit == 0
            else f"Process only the {format_number(args.limit)} first resources",
            option_name,
        )
        resources_to_process = list(take(args.limit, resources_to_process))
        _add_skipped_events(
            resources,
            resources_to_process,
            resource_event_by_id,
            option_name,
            on_event=on_event,
        )

    return resources_to_process


def _add_skipped_events(
    resources: Sequence[Resource],
    resources_to_process: Sequence[Resource],
    resource_event_by_id: Dict[ResourceId, ResourceEvent],
    option_name: str,
    on_event: OnEventCallback = None,
):
    """Add SKIPPED events for each resource not processed because of script options.

    Mutate ``resource_event_by_id``.
    """
    for resource in resources:
        if resource.id not in {r.id for r in resources_to_process}:
            event = ResourceEvent(
                id=resource.id,
                status=ResourceStatus.SKIPPED,
                duration=0,
                message=f"Resource is skipped because of {option_name} option",
            )
            resource_event_by_id[resource.id] = event
            if on_event:
                on_event(event)


def _validate_resources(
    all_resource_ids: Set[ResourceId], option_ids: Set[ResourceId], option_name: str
) -> Set[ResourceId]:
    """Check for invalid resources in script option.

    Log errors and return valid resources.
    """
    invalid_resources = option_ids - all_resource_ids
    if invalid_resources:
        logger.error(
            "%s passed to %s: %s",
            pluralize(
                len(invalid_resources),
                singular="invalid resource was",
                plural="invalid resources were",
            ),
            option_name,
            ", ".join(sorted(invalid_resources)),
        )
    valid_resources = option_ids - invalid_resources
    return valid_resources
