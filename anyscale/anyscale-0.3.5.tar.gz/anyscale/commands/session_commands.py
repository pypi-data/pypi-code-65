from typing import Any, Optional

import click

from anyscale.controllers.session_controller import SessionController


@click.command(name="down", help="Stop the current session.")
@click.argument("session-name", required=False, default=None)
@click.option(
    "--terminate", help="Terminate the session instead of stopping it.", is_flag=True
)
@click.option(
    "--workers-only", is_flag=True, default=False, help="Only destroy the workers."
)
@click.option(
    "--keep-min-workers",
    is_flag=True,
    default=False,
    help="Retain the minimal amount of workers specified in the config.",
)
@click.option("--delete", help="Delete the session after terminating.", is_flag=True)
@click.pass_context
def anyscale_stop(
    ctx: Any,
    session_name: Optional[str],
    terminate: bool,
    workers_only: bool,
    keep_min_workers: bool,
    delete: bool,
) -> None:
    session_controller = SessionController()
    session_controller.stop(
        session_name,
        terminate=terminate,
        workers_only=workers_only,
        keep_min_workers=keep_min_workers,
        delete=delete,
    )
