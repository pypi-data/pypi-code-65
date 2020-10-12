import warnings

import click

from . import __version__
from .task import task


@click.group(name="nominode")
@click.version_option(version=__version__, prog_name="nomnomdata-nominode")
def cli():
    """NomNomData Nominode CLI, used for the interacting with nominodes"""
    pass


cli.add_command(task)
