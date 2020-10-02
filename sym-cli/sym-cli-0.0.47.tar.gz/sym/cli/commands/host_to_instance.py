import click

from ..decorators import loses_interactivity, require_login
from ..helpers import boto
from ..helpers.global_options import GlobalOptions
from ..helpers.options import resource_argument
from .sym import sym


@sym.command(short_help="Get an Instance ID for a host")
@resource_argument
@click.argument("host")
@click.make_pass_decorator(GlobalOptions)
@loses_interactivity
@require_login
def host_to_instance(options: GlobalOptions, resource: str, host: str) -> None:
    client = options.create_saml_client(resource)
    click.echo(boto.host_to_instance(client, host))
