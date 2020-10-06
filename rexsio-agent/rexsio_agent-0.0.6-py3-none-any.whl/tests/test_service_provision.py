import unittest
from unittest import mock
from unittest.mock import mock_open, call, Mock

from agent.commands.service_provision import provision_service

get_base_service_path_mock = Mock()
get_base_service_path_mock.return_value = '/test/path/1234'


class TestServiceInstall(unittest.TestCase):

    @mock.patch("agent.commands.service_provision.RABBITMQ_PASS", "pass")
    @mock.patch('agent.commands.utils.get_base_service_path', get_base_service_path_mock)
    @mock.patch('agent.commands.service_provision.docker_compose_pull')
    @mock.patch('agent.commands.service_provision.docker_compose_up')
    @mock.patch('agent.commands.service_provision._get_docker_compose_file')
    @mock.patch('agent.commands.logger.info')
    @mock.patch('agent.commands.service_provision._generate_service_certificate')
    @mock.patch('json.dump')
    @mock.patch('builtins.open', new_callable=mock_open)
    @mock.patch('os.path')
    def test_secretary_provision_success(self, mock_dir, mock_config_file, mock_json, mock_cert, mock_logger,
                                         mock_request, mock_docker_compose_up, mock_docker_compose_pull):
        # given
        body = {"nodeServiceId": "id",
                "config": {
                    "key1": "value1",
                    "key2": "value2"},
                "dockerComposeUrl": "url",
                "serviceType": "secretary",
                "version": "v12"}

        mock_dir.isdir.return_value = True
        expected_config_content = {
            'key1': 'value1',
            'key2': 'value2',
            "rabbitmqPass": "pass"
        }
        # when
        provision_service(body)

        # then
        open_calls = [call('/test/path/1234/config/config.json', 'w'),
                      call().__enter__(),
                      call().__exit__(None, None, None)]
        mock_config_file.assert_has_calls(calls=open_calls, any_order=False)
        mock_json.assert_called_once_with(expected_config_content, mock_config_file.return_value.__enter__.return_value)
        mock_cert.assert_called_once_with('id')
        mock_request.assert_called_once_with(url='url', filename='/test/path/1234/docker-compose.yaml')
        mock_docker_compose_pull.assert_called_once_with('/test/path/1234/docker-compose.yaml')
        mock_docker_compose_up.assert_called_once_with('/test/path/1234/docker-compose.yaml')
        logger_calls = [call('Config updated: /test/path/1234/config/config.json'),
                        call('Docker compose file downloaded: /test/path/1234/docker-compose.yaml'),
                        call('Service secretary/id is running')]
        mock_logger.assert_has_calls(calls=logger_calls, any_order=False)

    @mock.patch("agent.commands.service_provision.RABBITMQ_PASS", "pass")
    @mock.patch('agent.commands.utils.get_base_service_path', get_base_service_path_mock)
    @mock.patch('agent.commands.service_provision.docker_compose_pull')
    @mock.patch('agent.commands.service_provision.docker_compose_up')
    @mock.patch('agent.commands.service_provision.find_smart_card_reader_address')
    @mock.patch('agent.commands.service_provision._get_docker_compose_file')
    @mock.patch('agent.commands.logger.info')
    @mock.patch('agent.commands.service_provision._generate_service_certificate')
    @mock.patch('json.dump')
    @mock.patch('builtins.open', new_callable=mock_open)
    @mock.patch('os.path')
    def test_notary_provision_success_without_private_key(self, mock_dir, mock_config_file, mock_json, mock_cert,
                                                          mock_logger, mock_request, mock_reader,
                                                          mock_docker_compose_up, mock_docker_compose_pull):
        # given
        body = {"nodeServiceId": "id",
                "config": {
                    "key1": "value1",
                    "key2": "value2",
                    "usePrivateKey": False},
                "dockerComposeUrl": "url",
                "serviceType": "notary-1",
                "version": "v12"}

        mock_dir.isdir.return_value = True
        expected_config_content = {
            'key1': 'value1',
            'key2': 'value2',
            "usePrivateKey": False,
            "rabbitmqPass": "pass"
        }

        mock_reader.return_value = '/dev/usb/reader/address'
        # when
        provision_service(body)

        # then
        mock_config_file.assert_has_calls([call('/test/path/1234/config/config.json', 'w'), ], any_order=True)
        mock_json.assert_called_once_with(expected_config_content, mock_config_file.return_value.__enter__.return_value)
        mock_cert.assert_called_once_with('id')
        mock_request.assert_called_once_with(url='url', filename='/test/path/1234/docker-compose.yaml')
        mock_docker_compose_pull.assert_called_once_with('/test/path/1234/docker-compose.yaml')
        mock_docker_compose_up.assert_called_once_with('/test/path/1234/docker-compose.yaml')
        logger_calls = [call('Config updated: /test/path/1234/config/config.json'),
                        call('Docker compose file downloaded: /test/path/1234/docker-compose.yaml'),
                        call('Smart card reader address added: /dev/usb/reader/address'),
                        call('Service notary-1/id is running')]
        mock_logger.assert_has_calls(calls=logger_calls, any_order=False)

    @mock.patch("agent.commands.service_provision.RABBITMQ_PASS", "pass")
    @mock.patch('agent.commands.utils.get_base_service_path', get_base_service_path_mock)
    @mock.patch('agent.commands.service_provision.docker_compose_pull')
    @mock.patch('agent.commands.service_provision.docker_compose_up')
    @mock.patch('agent.commands.service_provision.find_smart_card_reader_address')
    @mock.patch('agent.commands.service_provision._get_docker_compose_file')
    @mock.patch('agent.commands.logger.info')
    @mock.patch('agent.commands.service_provision._generate_service_certificate')
    @mock.patch('json.dump')
    @mock.patch('builtins.open', new_callable=mock_open)
    @mock.patch('os.path')
    def test_notary_provision_success_with_private_key(self, mock_dir, mock_config_file, mock_json, mock_cert,
                                                       mock_logger, mock_request, mock_reader, mock_docker_compose_up,
                                                       mock_docker_compose_pull):
        # given
        body = {"nodeServiceId": "id",
                "config": {
                    "key1": "value1",
                    "key2": "value2",
                    "usePrivateKey": True},
                "dockerComposeUrl": "url",
                "serviceType": "notary-1",
                "version": "v12"}

        mock_dir.isdir.return_value = True
        expected_config_content = {
            'key1': 'value1',
            'key2': 'value2',
            "usePrivateKey": True,
            "rabbitmqPass": "pass"
        }

        mock_reader.return_value = '/dev/usb/reader/address'
        # when
        provision_service(body)

        # then
        mock_config_file.assert_has_calls([call('/test/path/1234/config/config.json', 'w'), ], any_order=True)
        mock_json.assert_called_once_with(expected_config_content, mock_config_file.return_value.__enter__.return_value)
        mock_cert.assert_called_once_with('id')
        mock_request.assert_called_once_with(url='url', filename='/test/path/1234/docker-compose.yaml')
        mock_docker_compose_pull.assert_called_once_with('/test/path/1234/docker-compose.yaml')
        mock_docker_compose_up.assert_called_once_with('/test/path/1234/docker-compose.yaml')
        logger_calls = [call('Config updated: /test/path/1234/config/config.json'),
                        call('Docker compose file downloaded: /test/path/1234/docker-compose.yaml'),
                        call('Service notary-1/id is running')]
        mock_logger.assert_has_calls(calls=logger_calls, any_order=False)
