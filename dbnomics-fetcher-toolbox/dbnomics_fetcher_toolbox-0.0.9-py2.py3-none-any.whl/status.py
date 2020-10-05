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

"""Types and functions allowing to handle status file."""


import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional, Tuple, Union

import daiquiri
import jsonlines
import ujson as json
from pydantic import BaseModel, validator

STATUS_JSONL = "status.jsonl"

logger = daiquiri.getLogger(__name__)


class EventType(Enum):
    """The resulting state of processing a resource."""

    RESOURCE = "RESOURCE"
    RESOURCE_PART = "RESOURCE_PART"


class BaseEvent(BaseModel):
    """A base class for structured events."""

    type: EventType  # noqa
    id: str  # noqa
    emitted_at: datetime = None  # type: ignore
    duration: float
    message: Optional[str]

    @validator("emitted_at", pre=True, always=True)
    def set_emitted_at_now(cls, v):  # noqa
        return v or datetime.now().astimezone(timezone.utc)

    def to_json_data(self):
        """Return data as it would be encoded to JSON."""
        # This should be done by pydantic
        # Cf https://github.com/samuelcolvin/pydantic/issues/1008
        return json.loads(self.json(exclude_none=True))


class ResourceStatus(Enum):
    """The resulting state of processing a resource."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"


class ResourceEvent(BaseEvent):
    """Information gathered during the processing of a resource."""

    status: ResourceStatus
    type = EventType.RESOURCE  # noqa: A003


class PartStatus(Enum):
    """The resulting state of processing a resource part."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SPLIT = "SPLIT"


class PartEvent(BaseEvent):
    """Information gathered during the processing of a resource part."""

    resource_id: str
    status: PartStatus
    type = EventType.RESOURCE_PART  # noqa: A003
    series_count: Optional[int]  # only if status is SUCCESS
    split_dimension: Optional[str]  # only if status is SPLIT
    split_parts: Optional[Tuple[str, str]]  # only if status is SPLIT


@contextmanager
def open_status_writer(
    args: argparse.Namespace,
) -> Iterator[Callable[[BaseEvent], None]]:
    """Open a writer to create a ``status.jsonl`` file and fill it with events.

    Use it as a context manager.

    If ``--flush-status`` option was given, flush the file after appending each event.

    Example::

        with status.open_status_writer(args) as append_event:
            await process_resources(
                resources=resources,
                args=args,
                process_resource=process_resource,
                on_event=append_event,
                events=events,
            )
    """
    with jsonlines.open(
        args.target_dir / STATUS_JSONL,
        mode="a",
        flush=args.flush_status,
    ) as writer:

        def append_event(event: BaseEvent):
            writer.write(event.to_json_data())

        yield append_event


def load_events(
    target_dir: Path, dedupe: bool = True
) -> Optional[List[Union[ResourceEvent, PartEvent]]]:
    """Load events from ``status.jsonl`` expected to be found in ``target_dir``.

    If ``dedupe==True`` (default), the events are deduped by ``id``,
    keeping only the latest one in chronological order.
    Otherwise all the events are returned.
    """
    status_file = target_dir / STATUS_JSONL
    if not status_file.is_file():
        return None
    return load_events_from_file(status_file, dedupe=dedupe)


def load_events_from_file(
    file: Path, dedupe: bool = True
) -> List[Union[ResourceEvent, PartEvent]]:
    """Load events from ``file``.

    If ``dedupe==True`` (default), the events are deduped by ``id``, keeping only the
    latest one in chronological order. Otherwise all the events are returned.
    """
    events = iter_events(file)
    return dedupe_events(events) if dedupe else list(events)


def iter_events(file: Path) -> Iterator[Union[ResourceEvent, PartEvent]]:
    """Yield events from ``file``, ignoring events without or with invalid ``type``."""
    with jsonlines.open(file) as reader:
        for line_number, d in enumerate(reader.iter(), start=1):
            event_type = d.get("type")
            if event_type is None:
                logger.error(
                    "Event data %s line %d has no type", str(file), line_number
                )
                continue
            if event_type == EventType.RESOURCE.value:
                yield ResourceEvent.parse_obj(d)
            elif event_type == EventType.RESOURCE_PART.value:
                yield PartEvent.parse_obj(d)
            else:
                logger.error(
                    "Event data %s line %d has invalid type: %r",
                    str(file),
                    line_number,
                    event_type,
                )


def dedupe_events(
    events: Iterable[Union[ResourceEvent, PartEvent]]
) -> List[Union[ResourceEvent, PartEvent]]:
    """Yield events in chronological order, deduped by ``event.id``.

    Because the status file is an activity log, it can contain multiple items
    having the same event id. This function dedupes events by ``id`` by keeping
    the latest ones in chronological order.
    """
    event_by_id = {event.id: event for event in events}
    return sorted(event_by_id.values(), key=lambda event: event.emitted_at)
