from typing import Dict, List

import click
from psycopg2 import connect
from psycopg2._psycopg import connection as Connection

from pgdont.ruler import Ruler


def _get_config() -> str:
    return ''


def _get_connection(dsn: str) -> Connection:
    try:
        return connect(dsn=dsn)
    except Exception as e:
        print('An error occured : ', e)


def _report_formatter(reports: List[Dict]) -> None:
    for report in reports:
        if report:
            click.echo('='*79)
            click.echo(
                f'Rule : {report["rule"]}'
                '\n'
                f'URL : {report["url"]}'
                '\n'
                f'Details : {report["details"]}'
            )


@click.command()
@click.option('--dsn',
              help="DSN connection string to connect to the database",
              required=False,
              default=_get_config())
def cli(dsn: str) -> None:
    ruler = Ruler(_get_connection(dsn))
    ruler.load_rules()
    _report_formatter(ruler.process_all())
