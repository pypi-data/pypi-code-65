"""
ccsdoc main command line interface

\b
select one of the following actions:
- `parse`: create a catalogue of available commands in a given subsystem
- `convert`: convert the command catalog to a given extension
             needs the conversion tool `pandoc` installed
"""
import click

from ccsdoc.scripts import parse
from ccsdoc.scripts import convert


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, help=__doc__)
def cli():
    pass


cli.add_command(parse.main)
cli.add_command(convert.main)
