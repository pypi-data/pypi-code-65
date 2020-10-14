from asyncio import get_event_loop
from typing import Optional

import typer
from pydantic import BaseModel
from loguru import logger

from ..nats import FastNATS
from ..stan import FastSTAN
from ..utils import _import


app = typer.Typer()
app.is_stan = False


async def _start(subject: str, function):

    client = FastSTAN() if app.is_stan else FastNATS()

    client.subscribe(subject)(function)

    logger.debug(f"Connecting to NATS using client: {client}")
    await client.connect()
    logger.debug(f"Starting subscription on subject {subject}.")
    await client.start()


@app.command()
def start(
    subject: str = typer.Argument(..., help="Subject to subscribe to."),
    function: Optional[str] = typer.Option(None, help="Function to use as callback."),
):
    """Start a new subscrtion on any subject."""
    if function is None:

        class JSONDocument(BaseModel):
            class Config:
                extra = "allow"

        def default_callback(msg: JSONDocument):
            logger.info(f"Received new message: {msg}")

        _func = default_callback
    else:
        _func = _import(function)
    logger.debug(f"Successfully imported function {_func.__name__}.")
    loop = get_event_loop()
    loop.run_until_complete(_start(subject, _func))
    loop.run_forever()


if __name__ == "__main__":
    app()
