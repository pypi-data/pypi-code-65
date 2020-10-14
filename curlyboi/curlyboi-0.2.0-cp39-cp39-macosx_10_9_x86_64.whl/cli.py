# -*- coding: utf-8 -*-

import os

import click

from curlyboi import _curlyboi
from curlyboi.__version__ import __version__


@click.command("curlyboi")
@click.version_option(version=__version__)
@click.pass_context
def cli(*args, **kwargs):
    """A simple curlyboi game written in C using ncurses."""

    _curlyboi.game()


if __name__ == "__main__":
    cli()
