#!/usr/bin/env python

import click
# import ujson
from .. import utils
from .. import inputs
from .. import remote
from decimal import Decimal

import pandas as pd
pd.options.display.float_format = '{:,}'.format

NUMERIC_COLS = ["regt_buying_power", "equity", "daytrading_buying_power",
                "buying_power", "cash", "unrealized_pnl", "realized_pnl",
                "initial_margin", "maintenance_margin", "sma"]


def accounts_list(options):
    data = remote.api.get("/accounts")
    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    if not data:
        click.echo("\nNo accounts found.")
        return

    table_data = []
    for x in data:
        item = {
            "account id": data[x]["account_id"],
            "broker": "{broker} ({currency})".format(
                broker=data[x]["broker"].title(),
                currency=data[x]["currency"]
            ),
            "equity": data[x]["equity"],
            "realized_pnl": data[x]["realized_pnl"],
            "unrealized_pnl": data[x]["unrealized_pnl"]
        }
        try:
            item["equity"] = "{:,.2f}".format(Decimal(data[x]["equity"]))
        except:
            pass
        try:
            item["realized_pnl"] = "{:,.2f}".format(Decimal(data[x]["realized_pnl"]))
        except:
            pass
        try:
            item["unrealized_pnl"] = "{:,.2f}".format(Decimal(data[x]["unrealized_pnl"]))
        except:
            pass

        table_data.append(item)

    click.echo(utils.to_table(table_data))


def account_info(options):
    data = remote.api.get("/account/{account}".format(
        account=options.first("account")))

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    df = pd.DataFrame([data])
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def account_create(options):

    brokers = {}
    supported_brokers = remote.api.get("/brokers?tctl=true")
    for broker in supported_brokers:
        brokers[broker['name']] = broker

    click.echo("")
    name = ""
    while name == "":
        name = inputs.text("Account name")

    broker = inputs.option_selector(
        "Please select broker", list(brokers.keys()))
    broker = brokers.get(broker)

    paper_mode = False
    auth = {}
    # key = secret = account_id = None

    if broker["broker"] == "tradologics":
        paper_mode = True
    else:
        if broker.get("has_paper", False):
            paper_mode = inputs.confirm(
                "Use broker's paper account", default=True)

        if broker["broker"] == "ib":
            while not auth.get("key"):
                auth["key"] = inputs.text("Username")
            while not auth.get("secret"):
                auth["secret"] = inputs.hidden("Password")
            while not auth.get("account_id"):
                auth["account_id"] = inputs.hidden("Account ID")
        else:
            for key in broker["auth"]:
                while not auth.get(key):
                    auth[key] = inputs.hidden(
                        key.replace("_", " ").title().replace("Id", "ID"))

    payload = {
        "name": name,
        "paper": paper_mode,
        "auth": auth,
        "broker": broker["broker"]
    }

    # click.echo(utils.to_json(payload))
    data = remote.api.post("/accounts", json=payload)

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    utils.success_response(
        f"The broker account `{name}` ({broker['name']}) was added to your account.")

    df = pd.DataFrame([data])
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def account_update(options):

    account = remote.api.get("/account/{account}".format(
        account=options.first("account")))

    supported_brokers = remote.api.get("/brokers")
    for broker in supported_brokers:
        if broker["broker"] == account["broker"]:
            break

    click.echo(f"\nAccount's Broker: {broker['name']}\n")
    name = ""
    while name == "":
        name = inputs.text("New account name")

    paper_mode = False
    key = secret = account_id = None

    if broker["broker"] != "paper":
        if broker.get("has_paper", True):
            paper_mode = inputs.confirm(
                "Use broker's paper account", default=True)

        click.echo(
            "\nTo update credentials, enter new information (leave blank otherwise):\n")

        if broker["broker"] == "ib":
            key = inputs.text("Username")
            secret = inputs.hidden("Password")
            account_id = inputs.hidden("Account ID")
        else:
            key = inputs.hidden("Key (API key or Token)")
            secret = inputs.hidden("Secret (leave blank if using a token)")

    payload = {
        "name": name,
        "paper": paper_mode
    }
    if key or secret or account_id:
        payload["auth_info"] = {}
        if key:
            payload["auth_info"]["key"] = key
        if secret:
            payload["auth_info"]["secret"] = secret
        if account_id:
            payload["auth_info"]["account_id"] = account_id

    # click.echo(utils.to_json(payload))
    data = remote.api.patch(f"/account/{account['account_id']}", json=payload)

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    utils.success_response(
        f"The broker account `{name}` ({broker['name']}) was updated")

    df = pd.DataFrame([data])
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def account_delete(options):
    account = options.first("account")
    remote.api.delete("/account/{account}".format(
        account=options.first("account")))

    utils.success_response(
        f"The broker account `{account}` was removed from your account")
