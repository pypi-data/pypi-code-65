from typing import Optional

import click

from anyscale.api import get_api_client
from anyscale.client.openapi_client import StopSessionOptions  # type: ignore
from anyscale.client.openapi_client.api.default_api import DefaultApi  # type: ignore
from anyscale.project import (
    get_project_id,
    get_project_sessions,
    load_project_or_throw,
)
from anyscale.util import get_endpoint


class SessionController:
    def __init__(self, api_client: Optional[DefaultApi] = None):
        if api_client is None:
            api_client = get_api_client()
        self.api_client = api_client

    def stop(
        self,
        session_name: Optional[str],
        terminate: bool,
        delete: bool,
        workers_only: bool,
        keep_min_workers: bool,
    ) -> None:
        project_definition = load_project_or_throw()
        project_id = get_project_id(project_definition.root)
        sessions = get_project_sessions(project_id, session_name, self.api_client)
        terminate = terminate or delete

        if not session_name and len(sessions) > 1:
            raise click.ClickException(
                "Multiple active sessions: {}\n"
                "Please specify the one you want to stop with --session-name.".format(
                    [session["name"] for session in sessions]
                )
            )

        for session in sessions:
            # Stop the session and mark it as stopped in the database.
            self.api_client.stop_session_api_v2_sessions_session_id_stop_post(
                session.id,
                StopSessionOptions(
                    terminate=terminate,
                    workers_only=workers_only,
                    keep_min_workers=keep_min_workers,
                    delete=delete,
                ),
            )

        session_names = [session.name for session in sessions]
        session_names_str = ", ".join(session_names)
        url = get_endpoint(f"/projects/{project_id}")
        print(f"Session {session_names_str} stopping. View progress at {url}")
