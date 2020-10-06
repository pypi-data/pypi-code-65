import subprocess
from unittest import TestCase, mock

from agent.commands import shell_executor
from agent.exceptions.agent_error import AgentError


class Test(TestCase):
    def test_execute_shell_command__correct_behavior(self):
        # given
        subprocess.call = mock.MagicMock()
        # when
        shell_executor.execute_shell_command("command -f")
        # then
        subprocess.call.assert_called_with(["command", "-f"])

    def test_execute_shell_command__raises_AgentError_when_exception(self):
        # given
        subprocess.call = mock.MagicMock()
        subprocess.call.side_effect = subprocess.CalledProcessError(222, "command")
        # when then
        self.assertRaises(AgentError, shell_executor.execute_shell_command, "command")
