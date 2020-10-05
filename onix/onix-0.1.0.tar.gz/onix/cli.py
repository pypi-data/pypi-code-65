# -*- coding: utf-8 -*-

import click

from .__version__ import __version__


@click.command("onix")
@click.version_option(version=__version__)
@click.pass_context
def cli(*args, **kwargs):
    """Actually a snek!"""

    click.echo("Actually a snek!")
