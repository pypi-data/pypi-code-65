from asyncio import get_event_loop

import typer
from loguru import logger

from ..nats import FastNATS
from ..utils import _import


app = typer.Typer()


async def _start(subject: str, function):

    client = FastNATS()
    client.reply(subject)(function)

    logger.debug(f"Connecting to NATS using client: {client}")
    await client.connect()
    logger.debug("Starting service on subject {subject}.")
    await client.start()


@app.command()
def start(
    subject: str = typer.Argument(..., help="Subject to subscribe to."),
    function: str = typer.Option(..., help="Function to use as callback."),
):
    """Start a new service as a request/reply subscription."""
    _func = _import(function)
    logger.debug(f"Successfully imported function {_func.__name__}.")
    loop = get_event_loop()
    loop.run_until_complete(_start(subject, _func))
    loop.run_forever()


if __name__ == "__main__":
    app()
