import subprocess
from unittest import TestCase, mock

from agent.commands.uninstall import uninstall


class TestUninstallNode(TestCase):
    @mock.patch("agent.commands.uninstall.INSTALL_DIR", "/install/dir")
    @mock.patch("agent.commands.uninstall.ScheduledTaskManager.get_instance")
    @mock.patch("agent.commands.uninstall.ScheduledTaskManager.stop_executing")
    @mock.patch("agent.commands.uninstall.stop_rabbitmq")
    def test_uninstall_node(
        self, mock_stop_rabbitmq, mock_stop_executing, mock_get_instance
    ):
        # given
        task_manager_mock = mock.Mock()
        task_manager_mock.stop_executing = mock_stop_executing
        mock_get_instance.return_value = task_manager_mock

        subprocess.call = mock.MagicMock()

        # when
        uninstall()

        # then
        mock_stop_rabbitmq.assert_called_once()
        mock_stop_executing.assert_called_once()
        subprocess.call.assert_called_with(
            ["sudo", "/install/dir/uninstall.sh", "/install/dir", "rexsio"]
        )
