#!/usr/bin/env python

import click
import sys
import subprocess

from . import version
from . import inputs

from .env import ENVIRONMENT


def get_pip_newest_version(package):
    process = subprocess.Popen(
        ["pip", "install", f"{package}==xxx"], stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    return stderr.decode().split("(")[1].split(')')[0].split(',')[-1].strip()


@click.group()
def cli():
    pass


@cli.command()
def upgrade():
    """ Upgrade tctl to the latest version """

    click.echo("")
    package = "git+https://github.com/tradologics/tctl.git@dev"

    if ENVIRONMENT != "dev":
        package = "tctl"

        latest_version = get_pip_newest_version("tctl")
        curr_version = version.version.replace('.', '')
        new_version = latest_version.replace('.', '')
        if curr_version >= new_version:
            click.echo("You're using the latest version (tctl v. {v})".format(
                v=version.version))
            sys.exit(0)

        click.echo("""\nYou're running tctl version:  {curr}
    Latest version available is:  {v}\n""".format(
            curr=version.version, v=latest_version))

    up = inputs.confirm("Upgrade?", default=False)

    if not up:
        raise click.Abort()

    click.echo("\nUpgrading... ", nl=False)

    process = subprocess.Popen(
        ['pip', 'install', '--upgrade', '--no-cache-dir', package],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    stdout = stdout.decode()
    stderr = stderr.decode()

    if not stderr or "already up-to-date" in stdout:
        click.echo(click.style("SUCCESS", fg="green"))
        click.echo(f"\ntctl was upgraded to version {latest_version}")
        sys.exit()

    click.echo(click.style("FAILED\n", fg="red"))
    click.echo(stderr.replace("ERROR: ", "").strip())
