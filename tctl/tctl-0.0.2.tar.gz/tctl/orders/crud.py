#!/usr/bin/env python

import click
# import ujson
from .. import utils
from .. import inputs
from .. import remote
from decimal import Decimal
import re
import pandas as pd
pd.options.display.float_format = '{:,}'.format


def orders_list(options):
    strategy = options['strategy'][0]
    data = remote.api.get(f"/monitor/price/{strategy}")

    if options.get("raw"):
        if not data:
            click.echo("\n[]")
        else:
            click.echo(utils.to_json(data))
        return

    if not data:
        click.echo("\nNo orders found.")
        return

    table_data = []
    for item in data:
        table_data.append({
            "id": item["id"],
            "asset": item["asset"],
            "rule": item["rule"].replace("_", " ").title().replace(" Or ", " or "),
            "price": "{:,.2f}".format(Decimal(item["price"])),
            "strategies": len(item["strategies"])
        })
    click.echo(utils.to_table(table_data))


def order_create(options):
    click.echo("")

    side = ""
    while side == "":
        side = inputs.option_selector("Order side", [
            "Buy", "Sell"]).lower().replace(" ", "_")

    asset = ""
    while asset == "":
        asset = inputs.text(f"Asset to {side}").upper()

    qty = inputs.text(
        "Quantity",
        validate=lambda _, x: re.match(re.compile(r'(\d+)'), x))

    order_type = inputs.option_selector("Order type", [
        "Market", "Limit", "Stop", "Stop Limit"]).lower().replace(" ", "_")

    price = None
    if "limit" in order_type:
        price = inputs.text(
            "Price (leave blank for market order)",
            validate=lambda _, x: re.match(re.compile(r'(\d+(\.\d+)?)'), x))

    tif = inputs.option_selector("Time in force", [
        "DAY", "GTC", "OPG", "CLS", "IOC", "FOK"]).lower()

    extended_hours = not inputs.confirm(
        "Execute during regular market hours?", default=True)

    payload = {
        "asset": asset,
        "qty": int(qty),
        "side": side,
        "order_type": order_type,
        "tif": tif,
        "extended_hours": extended_hours,
    }
    if order_type == "limit":
        payload["limit_price"] = price
    elif order_type == "stop_limit":
        payload["stop_price"] = price

    strategies = {}
    supported_strategies = remote.api.get("/strategies")
    for strategy in supported_strategies:
        strategies[strategy['name']] = strategy["strategy_id"]

    selected_strategy = strategies[inputs.option_selector(
        "Associate with strategy", list(strategies.keys()))]

    if not selected_strategy:
        click.echo(click.style("\nFAILED", fg="red"))
        click.echo("You *must* be associate this order with a strategy.")

    accounts = {}
    supported_accounts = remote.api.get("/accounts")
    for key, account in supported_accounts.items():
        accounts[account['name']] = account["account_id"]
    selected_account = accounts[inputs.option_selector(
        "Execute on broker", list(accounts.keys()))]

    payload["strategy_id"] = selected_strategy
    payload["account_id"] = selected_account

    payload["comment"] = inputs.text("Comment (optional)")

    payload["submit"] = not inputs.confirm(
        "Submit order? (no will create an order that you can submit later)", default=True)

    print(payload)

    click.echo(utils.to_json(payload))
    data = remote.api.post(f"/orders", json=payload)

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    and_submitted = " and submitted" if payload["submit"] else ""
    utils.success_response(
        f"The order was created{and_submitted} successfully.")

    click.echo(f"Order Id: {data['id']}")

    df = pd.DataFrame([data])
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(
            df.T, missingval="-", showindex=True, showheaders=False))



def order_delete(options):
    monitor = options['monitor'][0]
    remote.api.delete("/monitor/{monitor}".format(
        monitor=options['monitor'][0]))

    utils.success_response(
        f"The monitor `{monitor}` was removed from your account")
