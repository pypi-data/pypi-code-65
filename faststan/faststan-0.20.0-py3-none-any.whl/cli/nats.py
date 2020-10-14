from asyncio import get_event_loop
from typing import Dict, Any
import typer

from loguru import logger

from ..nats import FastNATS
from .services import app as ServiceApp
from .subscriptions import app as SubscriptionsApp

app = typer.Typer()

app.add_typer(ServiceApp, name="service", help="Manage NATS services.")
app.add_typer(SubscriptionsApp, name="sub", help="Manage NATS subscriptions.")


async def _publish(subject: str, data: Dict[str, Any]) -> None:
    async with FastNATS() as client:
        logger.debug(f"Connected to NATS using client: {client}")
        logger.debug(f"Publishing on subject {subject} with data {data}")
        await client.publish_json(subject, data)


async def _request(subject: str, data: Dict[str, Any]) -> None:
    async with FastNATS() as client:
        logger.debug(f"Connected to NATS using client: {client}")
        logger.debug(f"Requesting reply on subject {subject} with data {data}")
        result = await client.request_json(subject, data)
        logger.debug(f"Received result: {result}")


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def pub(ctx: typer.Context, subject: str):
    """Publish a new message on NATS Streaming any subject."""
    is_key = True
    kwargs = {}
    for extra_arg in ctx.args:
        if is_key:
            key = extra_arg
            if key.startswith("--"):
                key = key[2:]
            elif key.startswith("-"):
                key = key[1:]
            is_key = False
            continue
        kwargs[key] = extra_arg
        is_key = True
    loop = get_event_loop()
    loop.run_until_complete(_publish(subject, kwargs))


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def req(ctx: typer.Context, subject: str):
    """Publish a new message on any subject."""
    is_key = True
    kwargs = {}
    for extra_arg in ctx.args:
        if is_key:
            key = extra_arg
            if key.startswith("--"):
                key = key[2:]
            elif key.startswith("-"):
                key = key[1:]
            is_key = False
            continue
        kwargs[key] = extra_arg
        is_key = True
    loop = get_event_loop()
    loop.run_until_complete(_request(subject, kwargs))


if __name__ == "__main__":
    app()
