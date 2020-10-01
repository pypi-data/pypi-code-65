from gzip import GzipFile

import click

from dagster import DagsterInstance, check
from dagster.cli.debug import DebugRunPayload
from dagster.cli.workspace import Workspace
from dagster.serdes import deserialize_json_to_dagster_namedtuple

from .cli import DEFAULT_DAGIT_HOST, DEFAULT_DAGIT_PORT, host_dagit_ui_with_workspace


@click.command(
    name="debug",
    help="Load dagit with an ephemeral instance loaded from a dagster debug export file.",
)
@click.argument("input_file", type=click.Path(exists=True))
def dagit_debug_command(input_file):
    click.echo("Loading {} ...".format(input_file))
    with GzipFile(input_file, "rb") as file:
        blob = file.read().decode()
        debug_payload = deserialize_json_to_dagster_namedtuple(blob)

        check.invariant(isinstance(debug_payload, DebugRunPayload))

        click.echo(
            "Creating instance from debug payload \n\trun_id: {} \n\tdagster version: {}".format(
                debug_payload.pipeline_run.run_id, debug_payload.version
            )
        )

    instance = DagsterInstance.ephemeral(preload=debug_payload)
    host_dagit_ui_with_workspace(
        workspace=Workspace([]),
        instance=instance,
        port=DEFAULT_DAGIT_PORT,
        port_lookup=True,
        host=DEFAULT_DAGIT_HOST,
        path_prefix="",
    )


def main():
    dagit_debug_command()  # pylint: disable=no-value-for-parameter
