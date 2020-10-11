import click
import sys

from . import version

# internals
from . import config
from . import brokers
from . import accounts
from . import assets
from . import strategies
from . import tradehooks
from . import monitors
from . import orders
from . import trading
from . import tokens


if "--version" in sys.argv or "-V" in sys.argv:
    click.echo("\ntctl {version}".format(version=version.version))
    click.echo("Copyrights (c) Tradologics, Inc.")
    click.echo("https://tradologics.com")
    sys.exit()


cli = click.CommandCollection(sources=[
    config.cli,
    brokers.cli,
    accounts.cli,
    assets.cli,
    strategies.cli,
    tradehooks.cli,
    monitors.cli,
    orders.cli,
    trading.cli,
    tokens.cli
])


__version__ = version.version
__author__ = "Tradologics, Inc"

__all__ = ['cli']
