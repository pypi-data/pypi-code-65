from unittest import TestCase, mock
from unittest.mock import call

from agent.commands.docker_commands import docker_compose_restart
from agent.exceptions.agent_error import AgentError


def return_exception_when_docker_compose_restart(command):
    if command == "docker-compose -f path restart":
        raise AgentError("expression", "message")


class Test(TestCase):
    @mock.patch('agent.commands.docker_commands.execute_shell_command')
    def test_docker_compose_restart_success(self, execute_shell_mock):
        # when
        docker_compose_restart("path")
        # then
        execute_shell_mock.assert_called_with("docker-compose -f path restart")

    @mock.patch('agent.commands.docker_commands.execute_shell_command')
    def test_docker_compose_restart__when_fails__runs_docker_compose_up(self, execute_shell_mock):
        # given
        execute_shell_mock.side_effect = return_exception_when_docker_compose_restart
        # when
        docker_compose_restart("path")
        # then
        execute_shell_mock.assert_has_calls(
            [call("docker-compose -f path restart"), call("docker-compose -f path up -d")])
