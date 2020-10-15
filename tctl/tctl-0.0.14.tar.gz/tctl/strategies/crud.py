#!/usr/bin/env python

import click
import re
from .. import utils
from .. import inputs
from .. import remote
# from decimal import Decimal


import pandas as pd
pd.options.display.float_format = '{:,}'.format

regex = re.compile(
    r'^https?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def strategies_list(options):
    data = remote.api.get("/strategies")
    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    if not data:
        click.echo("\nNo strategies found.")
        return

    click.echo(utils.to_table(data, hide=["url"]))


def strategy_info(options):
    data = remote.api.get("/strategy/{strategy}".format(
        strategy=options.first("strategy")))

    if data.get("as_tradelet", True):
        del data["url"]

    if options.get("raw"):
        if not data:
            click.echo("\n[]")
        else:
            click.echo(utils.to_json(data))
        return

    if not data:
        click.echo("\nNo strategies found.")
        return

    df = pd.DataFrame([data])
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def strategy_status(options):
    data = remote.api.get("/strategy/{strategy}/status".format(
        strategy=options.first("strategy")))

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    click.echo("\nStatus: {status}".format(status=data["status"]))


def strategy_log(options):
    data = remote.api.get("/strategy/{strategy}/logs".format(
        strategy=options.first("strategy")))

    lines = options.get("lines", [10])
    data["logs"] = data["logs"][-abs(int(lines[0])):]

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    if not data["logs"]:
        click.echo("\n[no logs]")
        return
    click.echo("\n" + "\n".join(data["logs"]))


def strategy_update(options):

    strategy = remote.api.get("/strategy/{strategy}".format(
        strategy=options.first("strategy")))

    click.echo()
    name = inputs.text(f"Name [{strategy['name']}]")
    description = inputs.text(f"Description [{strategy['description']}]")
    mode = inputs.option_selector(
        f"Mode [{strategy['mode']}]", ["Backtest", "Paper", "Broker"])

    data = remote.api.patch(
        "/strategy/{strategy}".format(strategy=options.first("strategy")),
        json={
            "name": name,
            "description": description,
            "mode": mode.lower()
        })

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    utils.success_response(
        f"The strategy `{name}` was updated")

    df = pd.DataFrame([data])
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def strategy_delete(options):
    strategy = options.first("strategy")
    remote.api.delete("/strategy/{strategy}".format(strategy=strategy))

    utils.success_response(
        f"The strategy `{strategy}` was removed from your account")


def strategy_set_mode(options):

    strategy = remote.api.get("/strategy/{strategy}".format(
        strategy=options.first("strategy")))

    mode = options.first("mode")
    if mode not in ["backtest", "paper", "broker"]:
        click.echo("\nCurrent mode: {mode}".format(mode=strategy["mode"]))
        click.echo()
        mode = inputs.option_selector(
            "New mode", [strategy["mode"].title()] + [
                mode.title() for mode in [
                    "backtest", "paper", "broker"
                ] if mode != strategy["mode"]
            ])

    if mode.lower() == strategy["mode"]:
        click.echo(f"Aborted! The strategy mode was unchanged ({mode}).")
        return

    data = remote.api.patch(
        "/strategy/{strategy}".format(strategy=options.first("strategy")),
        json={
            "mode": mode.lower()
        })

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    utils.success_response(
        f"The strategy's mode was chaned to `{mode}`")


def strategy_start(options):
    data = {
        "message": "Tradelet deploy initialized. You can check status on '/strategy/my-tradelet-strategy-new/status/' and check logs on '/strategy/my-tradelet-strategy-new/logs/'"
    }

    strategy = options.first("strategy")
    data = remote.api.post(
        "/strategy/{strategy}/start".format(strategy=strategy))

    if "Tradelet" in data["message"]:
        data["message"] = [
            "Tradelet deploy initialized...\n",
            f"  - Check status using `tctl strategies status --strategy {strategy}`",
            f"  - Deploy log is available via `tctl strategies log --strategy {strategy}`",
        ]
    else:
        data["message"] = ["Strategy starting.."]

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    utils.success_response("\n".join(data["message"]))


def strategy_stop(options):
    strategy = options.first("strategy")
    remote.api.post(
        "/strategy/{strategy}/stop".format(strategy=strategy))

    utils.success_response(f"The strategy `{strategy}` was stopped.")


def strategy_create(options):
    click.echo()
    name = ""
    while name == "":
        name = inputs.text("Strategy name")
    description = inputs.text("Description (leave blank for none)")
    mode = inputs.option_selector(
        "Mode", ["Backtest", "Paper", "Broker"])

    as_tradelet = inputs.confirm(
        "Host strategy on Tradologics?", default=True)
    url = None
    if not as_tradelet:
        while url is None:
            url = inputs.text(
                "Strategy URL", validate=lambda _, x: re.match(regex, x))

    payload = {
        "name": name,
        "description": description,
        "mode": mode.lower(),
        "as_tradelet": as_tradelet,
    }
    if url:
        payload["url"] = url

    data = remote.api.post("/strategies", json=payload)

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    utils.success_response(
        f"The strategy `{name}` ({mode}) was added to your account.")

    cols = ['name', 'strategy_id', 'description', 'as_tradelet', 'mode']
    if not as_tradelet:
        cols.append("url")
    df = pd.DataFrame([data])[cols]
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def strategy_stats(options):
    error = {
        "id": "unprocessable_request",
        "message": "Not supported yet via tctl"
    }
    click.echo(click.style("\nFAILED", fg="red"), nl=False)
    click.echo(" (status code 422):")
    click.echo(utils.to_json(error))
