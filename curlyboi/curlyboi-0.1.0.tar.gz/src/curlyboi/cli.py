# -*- coding: utf-8 -*-

import os

import click

from ._curlyboi import game
from curlyboi.__version__ import __version__


@click.command("curlyboi")
@click.version_option(version=__version__)
@click.pass_context
def cli(*args, **kwargs):
    """Actually a snek!"""

    game()


if __name__ == "__main__":
    cli()
