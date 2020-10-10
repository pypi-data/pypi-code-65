#!/usr/bin/env python

import click
from .. import utils
from .. import remote
import urllib
from datetime import datetime
import pandas as pd
pd.options.display.float_format = '{:,}'.format


def exchanges_list(options):
    data = remote.api.get("/exchanges")

    if options.get("raw"):
        click.echo_via_pager(utils.to_json(data))
        return

    df = pd.DataFrame(data)

    df.sort_values("name", inplace=True)
    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df))


def exchange_info(options):
    endpoint = "/exchange/{identifier}".format(
        identifier=options.first("exchange").upper())

    data = remote.api.get(endpoint)

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    df = pd.DataFrame([data])[:1]

    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(df.T, showindex=True, showheaders=False))


def exchange_calendar(options):
    exchange = options.get("exchange")[0].upper()
    start, _ = utils.parse_date(
        options.get("start", [datetime.now().strftime("%Y-%m-%d")])[0])
    end, _ = utils.parse_date(
        options.get("end", [datetime.now().strftime("%Y-%m-%d")])[0])

    start = urllib.parse.quote(start)
    end = urllib.parse.quote(end)
    data = remote.api.get(f"/calendar/{exchange}/{start}/{end}")

    if options.get("raw"):
        click.echo(utils.to_json(data))
        return

    df = pd.DataFrame(data["calendar"]).T

    del data["calendar"]
    exh_df = pd.DataFrame([data])
    exh_df.columns = [col.replace("_", " ").title() for col in exh_df.columns]
    exh_df = exh_df.T
    exh_df.columns = [""]

    click.echo(exh_df)
    click.echo("\nCalendar:")

    df.columns = [col.replace("_", " ").title() for col in df.columns]
    click.echo(utils.to_table(
        df[["Market Open", "Market Close"]], showindex=True).lstrip())
