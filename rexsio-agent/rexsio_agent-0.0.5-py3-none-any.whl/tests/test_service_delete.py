from unittest import TestCase, mock
from unittest.mock import Mock

from agent.commands.service_delete import delete_service


class Test(TestCase):

    @mock.patch('agent.commands.service_delete.get_base_service_path', return_value='/test/path/1234')
    @mock.patch('agent.commands.service_delete.ScheduledTaskManager.get_instance')
    @mock.patch('agent.commands.service_delete.ScheduledTaskManager.stop_executing')
    @mock.patch('agent.commands.service_delete.ScheduledTaskManager.start_executing')
    @mock.patch('agent.commands.service_delete.docker_compose_down')
    @mock.patch('agent.commands.service_delete.shutil.rmtree')
    def test_service_deletion(self,
                              mock_shutil_rmtree,
                              mock_docker_compose_down,
                              mock_start_executing,
                              mock_stop_executing,
                              mock_get_instance,
                              mock_get_base_service_path):
        body = {'nodeServiceId': '1234'}
        protocol_mock = Mock()
        protocol_mock.start_executing = mock_start_executing
        protocol_mock.stop_executing = mock_stop_executing
        mock_get_instance.return_value = protocol_mock

        delete_service(body)

        mock_shutil_rmtree.assert_called_with('/test/path/1234', ignore_errors=True)
        mock_start_executing.assert_called_once()
        mock_stop_executing.assert_called_once()
        mock_docker_compose_down.assert_called_with('/test/path/1234/docker-compose.yaml')