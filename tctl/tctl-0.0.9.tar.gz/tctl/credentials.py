#!/usr/bin/env python

import dotenv
import click
import uuid
import os
import sys

from base64 import b64encode as _b64encode, b64decode as _b64decode
import uuid as _uuid

from pathlib import Path

# internals
from . import remote
from . import terminal
from . import inputs


_token = {
    "id": _uuid.getnode(),
    "name": "tctl-{uuid}--auto-generated".format(uuid=_uuid.getnode())
}

env_path = Path.home() / '.tradologics'

if not Path.exists(env_path):
    Path.touch(env_path)

dotenv.load_dotenv(env_path)


def delete():
    Path.unlink(env_path)
    click.echo("\n")
    confirm = inputs.confirm(
        "Are you sure you want to delete your credentials?", default=False)
    if not confirm:
        raise click.Abort()

    click.echo("\nDeleting... ", nl=False)
    click.echo(click.style("SUCCESS", fg="green"))
    click.echo("NOTE: tctl will need to be re-configured in order to work.")
    sys.exit(0)


def obfuscate(byt, password):
    mask = password.encode()
    lmask = len(mask)
    return bytes(c ^ mask[i % lmask] for i, c in enumerate(byt))


def encrypt(txt):
    return _b64encode(obfuscate(txt.encode(), hex(_token['id']))).decode()


def decrypt(txt):
    return obfuscate(_b64decode(txt.encode()), hex(_token['id'])).decode()


def config(source=None):
    click.echo(terminal.prompt)

    # if message:
    #     click.echo(message)
    #     click.echo("-----------------------------------------------------\n")

    dotenv.load_dotenv(env_path, verbose=True)
    no_token = not os.getenv("TOKEN")

    if no_token:
        click.echo("HELLO 👋")

        if source != "config":
            click.echo("""
tctl isn't configured on this machine yet.

Please have your API Key and Secret Key handy in
order to configure tctl.

Let's get started...

-----------------------------------------------------
""")
        else:
            click.echo("""
tctl (Tradologics' Controller) helps you access
and control various aspects of your account.

To get started, make sure you have your API Key
and Secret Key handy in order to configure tctl.

Let's get started...

-----------------------------------------------------

""")

    else:
        click.echo("Current configuration: {custoemr_name}".format(
            custoemr_name=os.getenv("NAME")))
        click.echo("(Customer ID: {customer_id})\n".format(
            customer_id=os.getenv("CUSTOMER_ID")))

        update = inputs.confirm("Replace it with a new one?", default=False)
        if not update:
            raise click.Abort()

    api_key = inputs.text("API Key     ")
    api_secret = inputs.hidden("API Secret  ")

    click.echo("\nValidating... ", nl=False)

    headers = {
        "TGX-API-KEY": api_key,
        "TGX-API-SECRET": api_secret
    }

    tokens = remote.api.get("/tokens?obfuscated=false", headers=headers)

    tctl_token = None
    for token in tokens:
        if token["name"] == _token["name"]:
            tctl_token = token.get("token")
            break

    if not tctl_token:
        res = remote.api.post(
            "/token",
            json={"name": _token['name'], "ttl": -1},
            headers=headers)

        tctl_token = res.get("token")

    # write token
    dotenv.set_key(env_path, "TOKEN", encrypt(tctl_token))

    # get custoemer data
    res = remote.api.get(
        "/me", headers=remote.bearer_token())

    for key in ["name", "email", "customer_id"]:
        dotenv.set_key(env_path, key.upper(), res.get(key))

    click.echo(click.style("SUCCESS\n", fg="green"))
    click.echo("tctl is now configured! 🎉")

    if source != "config":
        click.echo("\nPlease run your command again")
