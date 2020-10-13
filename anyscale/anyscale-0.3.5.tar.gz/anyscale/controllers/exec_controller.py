import json
from shlex import quote
import subprocess
import sys
import tempfile
from typing import List, Tuple

import click
from ray.autoscaler._private.commands import rsync
import ray.scripts.scripts as autoscaler_scripts

from anyscale.api import get_api_client
from anyscale.client.openapi_client.api.default_api import DefaultApi  # type: ignore
from anyscale.client.openapi_client.models.execute_shell_command_options import (  # type: ignore
    ExecuteShellCommandOptions,
)
from anyscale.cluster_config import (  # noqa: N812
    add_anyscale_node_provider as _DO_NOT_USE_add_anyscale_node_provider,
    get_cluster_config,
)
import anyscale.conf
from anyscale.project import get_project_id, get_project_session, load_project_or_throw
from anyscale.util import execution_log_name


class ExecController(object):
    def __init__(self, api_client: DefaultApi = None):
        if api_client is None:
            api_client = get_api_client()
        self.api_client = api_client

    def anyscale_exec(
        self,
        session_name: str,
        screen: bool,
        tmux: bool,
        port_forward: Tuple[int],
        sync: bool,
        stop: bool,
        commands: List[str],
    ) -> None:
        session_name, session_id = self._get_session_name_and_id(session_name)

        # Create a placeholder session command ID
        session_command = self.api_client.execute_interactive_command_api_v2_sessions_session_id_execute_interactive_command_post(
            session_id=session_id,
            execute_shell_command_options=ExecuteShellCommandOptions(
                shell_command=" ".join(commands)
            ),
        ).result
        session_command_id = session_command.command_id
        directory_name = session_command.directory_name

        remote_command = self._generate_remote_command(
            session_command_id, commands, directory_name, stop
        )

        cluster_config = get_cluster_config(session_name, self.api_client)
        cluster_config = _DO_NOT_USE_add_anyscale_node_provider(
            cluster_config, session_id
        )

        with tempfile.NamedTemporaryFile(mode="w") as config_file:
            json.dump(cluster_config, config_file)
            config_file.flush()
            config_file_path = config_file.name

            # Rsync file mounts if sync flag is set
            if sync:
                rsync(
                    config_file.name,
                    source=None,
                    target=None,
                    override_cluster_name=None,
                    down=False,
                    all_nodes=True,
                )

            command = [
                sys.executable,
                autoscaler_scripts.__file__,
                "exec",
                config_file_path,
                remote_command,
                "--screen" if screen else "",
                "--tmux" if tmux else "",
                "--stop" if stop else "",
                "--cluster-name",
                "{}".format(cluster_config["cluster_name"]),
            ]
            for port in list(port_forward):
                command.extend(["-p", str(port)])
            command_lst = [c for c in command if c]

            subprocess.check_call(command_lst, env=anyscale.ANYSCALE_ENV)  # noqa: B1

        if tmux or screen:
            launched_in_mode = "tmux" if tmux else "screen"
            # TODO(simon): change the message to anyscale attach when implemented
            click.echo(
                "Command launched in {mode}, use `anyscale ray attach {name} --{mode}` to check status.".format(
                    mode=launched_in_mode, name=session_name
                )
            )

    def _get_session_name_and_id(self, session_name: str) -> Tuple[str, str]:
        project_definition = load_project_or_throw()
        project_id = get_project_id(project_definition.root)
        session = get_project_session(project_id, session_name, self.api_client)

        return session.name, session.id

    def _generate_remote_command(
        self,
        session_command_id: str,
        commands: List[str],
        directory_name: str,
        stop: bool,
    ) -> str:
        # Save the PID of the command so we can kill it later.
        shell_command_prefix = (
            "echo $$ > {execution_log_name}.pid; "
            "export ANYSCALE_HOST={anyscale_host}; "
            "export ANYSCALE_SESSION_COMMAND_ID={session_command_id}; ".format(
                execution_log_name=execution_log_name(session_command_id),
                anyscale_host=anyscale.conf.ANYSCALE_HOST,
                session_command_id=session_command_id,
            )
        )

        # Note(simon): This section is largely similar to the server side exec command but simpler.
        # We cannot just use the server command because we need to buffer the output to
        # user's terminal as well and handle interactivity.
        redirect_to_dev_null = "&>/dev/null"
        shell_command = shell_command_prefix + " ".join(commands)
        remote_command = (
            "touch {execution_log_name}.out; "
            "touch {execution_log_name}.err; "
            "cd ~/{directory_name}; "
            "script -q -e -f -c {shell_command} {execution_log_name}.out; "
            "echo $? > {execution_log_name}.status; "
            "ANYSCALE_HOST={anyscale_host} anyscale session "
            "upload_command_logs --command-id {session_command_id} {redirect_to_dev_null}; "
            "ANYSCALE_HOST={anyscale_host} anyscale session "
            "finish_command --command-id {session_command_id} {stop_cmd} {redirect_to_dev_null}; ".format(
                directory_name=directory_name,
                execution_log_name=(execution_log_name(session_command_id)),
                anyscale_host=anyscale.conf.ANYSCALE_HOST,
                session_command_id=session_command_id,
                stop_cmd="--stop" if stop else "",
                shell_command=quote(shell_command),
                redirect_to_dev_null=redirect_to_dev_null,
            )
        )

        return remote_command
