import shlex
import subprocess

from agent.exceptions.agent_error import AgentError


def execute_shell_command(command):
    try:
        subprocess.call(shlex.split(command))
    except subprocess.CalledProcessError as err:
        raise AgentError(expression=command, message=err.output)
