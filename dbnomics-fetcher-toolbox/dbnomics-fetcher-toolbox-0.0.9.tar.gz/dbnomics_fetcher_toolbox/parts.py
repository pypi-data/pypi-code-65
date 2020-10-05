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

"""Functions handling resource parts."""

import argparse
import asyncio
import collections
import hashlib
import json
import statistics
import time
from typing import Awaitable, Callable, Deque, Dict, List, Sequence, Tuple

import daiquiri
from contexttimer import Timer
from humanfriendly import format_timespan, pluralize
from toolz.itertoolz import first

from .resources import Resource
from .status import EventType, PartEvent, PartStatus

logger = daiquiri.getLogger(__name__)


class SplitOneDimension(Exception):
    """Raise this exception to trigger a split on one dimension.

    In particular raise it from the ``process_resource`` callback of
    :func:`dbnomics_fetcher_toolbox.resources.process_resources`.
    """


Code = str
ValueCodes = List[Code]
Dimensions = Dict[Code, ValueCodes]


def dimensions_to_str(dimensions: Dimensions, is_initial_dimensions: bool) -> str:
    """Convert ``dimensions`` to ``str``.

    A dimension ``dict`` is generally too large and makes logs difficult to read.
    This method returns a shorter string to represent dimensions.

    :param is_initial_dimensions: if ``True`` return ``"all"``, otherwise compute
        a hash of ``dimensions``.
    """
    if is_initial_dimensions:
        return "all"
    dimensions_str = json.dumps(dimensions, sort_keys=True, ensure_ascii=False)
    # The hash is not meant to be secure, but just a shortcut to represent the dict.
    return hashlib.md5(dimensions_str.encode("utf-8")).hexdigest()  # noqa: DUO130


def select_first_alphabetic(candidates: Dimensions) -> Code:
    """Select the first dimension in alphabetic order."""
    return first(sorted(candidates.keys()))


def select_median_low(candidates: Dimensions) -> Code:
    """Select the dimension having the "median low" number of values.

    To avoid both:

    * the one with the least values because it has a higher probability
      to return too many results
    * the one with the most values because it could lead to URL too long
    """
    return statistics.median_low(  # type: ignore
        (len(v), k) for k, v in candidates.items()
    )[1]


ProcessPartCallback = Callable[[Dimensions, str, bool], Awaitable[None]]
OnEventCallback = Callable[[PartEvent], None]
DimensionsToStrCallback = Callable[[Dimensions, bool], str]
SelectSplitCandidateCallback = Callable[[Dimensions], Code]


async def process_parts(
    resource: Resource,
    args: argparse.Namespace,
    initial_dimensions: Dimensions,
    process_part: ProcessPartCallback,
    on_event: OnEventCallback = None,
    events: Sequence[PartEvent] = None,
    dimensions_to_str: DimensionsToStrCallback = dimensions_to_str,
    select_split_candidate: SelectSplitCandidateCallback = select_median_low,
):
    """Process a resource by processing its parts.

    ``process_part`` can raise a :exc:`SplitOneDimension` exception,
    meaning that the current part must be split on one dimension.
    """
    t0 = time.time()

    is_initial_dimensions = True
    depth = 0
    deque: Deque[Tuple[Dimensions, bool, int]] = collections.deque(
        [(initial_dimensions, is_initial_dimensions, depth)]
    )

    part_event_by_id = {
        event.id: event
        for event in events or []
        if event.type == EventType.RESOURCE_PART and event.resource_id == resource.id
    }

    part_number = 0

    while deque:
        part_number += 1

        dimensions, is_initial_dimensions, depth = deque.pop()
        dimensions_str = dimensions_to_str(dimensions, is_initial_dimensions)

        # Skip previous executed steps if "events" sequence was given.
        event = part_event_by_id.get(dimensions_str)
        if (
            not args.force
            and event is not None
            and (not args.retry_failed or event.status != PartStatus.FAILURE)
        ):
            logger.debug(
                "Skipping part %r because it has already been processed (%s)",
                event.id,
                event.status.value,
                resource=resource.id,
                depth=depth,
                part_number=part_number,
            )
            if event.status == PartStatus.SPLIT:
                _, part1, part2 = split(dimensions, select_split_candidate)
                deque.extend([(part2, False, depth + 1), (part1, False, depth + 1)])
            continue

        logger.info(
            "Processing part %r",
            dimensions_str,
            resource=resource.id,
            depth=depth,
            part_number=part_number,
        )

        with Timer() as t:
            try:
                if asyncio.iscoroutinefunction(process_part):
                    await process_part(
                        dimensions, dimensions_str, is_initial_dimensions
                    )
                else:
                    process_part(dimensions, dimensions_str, is_initial_dimensions)
            except SplitOneDimension:
                code, part1, part2 = split(dimensions, select_split_candidate)
                part1_str = dimensions_to_str(part1, False)
                part2_str = dimensions_to_str(part2, False)
                if on_event:
                    on_event(
                        PartEvent(
                            resource_id=resource.id,
                            id=dimensions_str,
                            duration=t.elapsed,
                            status=PartStatus.SPLIT,
                            split_dimension=code,
                            split_parts=(part1_str, part2_str),
                        )
                    )
                logger.debug(
                    "Split requested after %s, selecting dimension %r (%s) "
                    "and creating 2 parts: %r (%s for %r) and %r (%s for %r)",
                    format_timespan(t.elapsed),
                    code,
                    pluralize(len(dimensions[code]), "value"),
                    part1_str,
                    pluralize(len(part1[code]), "value"),
                    code,
                    part2_str,
                    pluralize(len(part2[code]), "value"),
                    code,
                    resource=resource.id,
                    depth=depth,
                    part_number=part_number,
                )
                deque.extend([(part2, False, depth + 1), (part1, False, depth + 1)])
            except Exception as exc:
                if on_event:
                    on_event(
                        PartEvent(
                            resource_id=resource.id,
                            id=dimensions_str,
                            duration=t.elapsed,
                            status=PartStatus.FAILURE,
                            message=str(exc),
                        )
                    )
                logger.error(
                    "Error processing part after %s",
                    format_timespan(t.elapsed),
                    resource=resource.id,
                    depth=depth,
                    part_number=part_number,
                )
                raise
            else:
                if on_event:
                    on_event(
                        PartEvent(
                            resource_id=resource.id,
                            id=dimensions_str,
                            duration=t.elapsed,
                            status=PartStatus.SUCCESS,
                        )
                    )
                logger.debug(
                    "Processed part in %s",
                    format_timespan(t.elapsed),
                    resource=resource.id,
                    depth=depth,
                    part_number=part_number,
                )

    logger.debug(
        "All parts processed in %s with a total of %s",
        format_timespan(time.time() - t0),
        pluralize(part_number, "step"),
        resource=resource.id,
    )


def split(
    dimensions: Dimensions, select_candidate: SelectSplitCandidateCallback
) -> Tuple[Code, Dimensions, Dimensions]:
    """Split ``dimensions``.

    Raise ``ValueError`` if ``dimensions`` are not splittable,
    i.e. all dimensions have one code.
    """
    code, value_codes1, value_codes2 = split_one_dimension(dimensions, select_candidate)
    part1 = {**dimensions, code: value_codes1}
    part2 = {**dimensions, code: value_codes2}
    return code, part1, part2


def split_one_dimension(
    dimensions: Dimensions, select_candidate: SelectSplitCandidateCallback
) -> Tuple[Code, List[Code], List[Code]]:
    """Choose a splittable dimension and split its codes in 2 sub-lists.

    Candidates are dimensions having more than one value code.

    Raise ``ValueError`` if ``dimensions`` are not splittable,
    i.e. all dimensions have one code.

    >>> split_one_dimension({}, select_median_low)
    Traceback (most recent call last):
        ...
    ValueError: No dimension defined, can't split
    >>> split_one_dimension({'FREQ': ['A']}, select_median_low)
    Traceback (most recent call last):
        ...
    ValueError: All dimensions have one value, can't split more
    >>> split_one_dimension({'FREQ': ['A'], 'COUNTRY': ['FR']}, select_median_low)
    Traceback (most recent call last):
        ...
    ValueError: All dimensions have one value, can't split more
    >>> split_one_dimension({'FREQ': ['A', 'Q']}, select_median_low)
    ('FREQ', ['A'], ['Q'])
    >>> split_one_dimension({'FREQ': ['A', 'Q'], 'COUNTRY': ['FR']}, select_median_low)
    ('FREQ', ['A'], ['Q'])
    >>> split_one_dimension({'FREQ': ['A', 'Q'], 'COUNTRY': ['FR', 'DE']},
    ...                     select_median_low)
    ('COUNTRY', ['FR'], ['DE'])
    >>> split_one_dimension({'FREQ': ['A', 'Q'], 'COUNTRY': ['FR', 'DE', 'IT']},
    ...                     select_median_low)
    ('FREQ', ['A'], ['Q'])
    """
    if not dimensions:
        raise ValueError("No dimension defined, can't split")

    candidates = {k: v for k, v in dimensions.items() if len(v) > 1}
    if not candidates:
        raise ValueError("All dimensions have one value, can't split more")

    code = select_candidate(candidates)
    value_codes = dimensions[code]

    half = len(value_codes) // 2
    value_codes1 = value_codes[:half]
    value_codes2 = value_codes[half:]
    return code, value_codes1, value_codes2
