import os
import uuid
from asyncio import get_event_loop
from typing import Dict, Any
import typer

from loguru import logger

from ..stan import FastSTAN
from .subscriptions import app as SubscriptionsApp

app = typer.Typer()

SubscriptionsApp.is_stan = True

app.add_typer(
    SubscriptionsApp, name="sub", help="Manager NATS streaming subscriptions."
)


async def _publish(subject: str, data: Dict[str, Any]) -> None:
    os.environ["client"] = str(uuid.uuid4())
    async with FastSTAN() as client:
        logger.debug(f"Connected to NATS using client: {client}")
        logger.debug(f"Publishing on subject {subject} with data {data}")
        await client.publish_json(subject, data)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def pub(ctx: typer.Context, subject: str):
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
    loop.run_until_complete(_publish(subject, kwargs))


if __name__ == "__main__":
    app()
