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

"""Utility functions for ``aiohttp``."""

import argparse
import asyncio
import os
from dataclasses import dataclass
from typing import AsyncIterator

import daiquiri
from aiohttp import ClientResponse, ClientSession, TraceConfig

logger = daiquiri.getLogger(__name__)


def get_trace_config() -> TraceConfig:
    """Get a ``TraceConfig`` instance configured to log ``aiohttp`` HTTP requests."""

    async def on_request_start(session: ClientSession, trace_config_ctx, params):
        logger.debug("Starting %s request: %s", params.method, params.url)

    trace_config = TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    return trace_config


def add_arguments_for_chunks(parser: argparse.ArgumentParser):
    """Add arguments to ``parser`` to be used with :func:`iter_chunks_with_timeout`."""
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=os.getenv("CHUNK_SIZE", 1024),
        help="size of a chunk in bytes to read when using HTTP requests in stream mode",
    )
    parser.add_argument(
        "--chunk-timeout",
        type=float,
        default=os.getenv("CHUNK_TIMEOUT", 5),
        help="max time in seconds to wait for a chunk when using HTTP requests "
        "in stream mode",
    )


@dataclass
class ChunkTimeoutError(Exception):
    """Chunk timeout error.

    Exception raised by :func:`iter_chunks_with_timeout` when a chunk is too long
    to download.

    :param bytes_count: number of bytes downloaded with the previous chunks
    """

    bytes_count: int


async def iter_chunks_with_timeout(
    response: ClientResponse, args: argparse.Namespace
) -> AsyncIterator[bytes]:
    """Raise :exc:`ChunkTimeoutError` if a timeout occurs while downloading a chunk.

    This allows to handle servers that suddenly stop sending data,
    without having to wait for the global request timeout
    or an HTTP error like 104 "Connection reset by peer".
    """
    bytes_count = 0
    while True:
        try:
            chunk = await asyncio.wait_for(
                response.content.read(args.chunk_size), timeout=args.chunk_timeout
            )
        except asyncio.TimeoutError as exc:
            raise ChunkTimeoutError(bytes_count) from exc
        if not chunk:
            break
        yield chunk
        bytes_count += len(chunk)
