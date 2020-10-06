from unittest import mock
from unittest.case import TestCase

from agent.commands.service_status import check_service_statuses


class MockedClient:
    def __init__(self, *containers):
        self.containers = MockedContainerList(*containers)


class MockedContainerList:
    def __init__(self, *containers):
        self.container_list = [*containers]

    def list(self, all, filters):
        name = filters['name']
        container_list = self.container_list
        return [container for container in container_list if name in container.name]


class MockedContainer:
    def __init__(self, name, status):
        self.name = name
        self.status = status


class TestServiceStatus(TestCase):

    @mock.patch('docker.from_env')
    @mock.patch('agent.commands.service_status.get_services_id_list')
    def test_check_service_statuses(self, mock_id_list, mock_containers):
        mock_id_list.return_value = ['Id1', 'id-2']
        mock_containers.return_value = MockedClient(MockedContainer(name='id1_name', status='running'),
                                                    MockedContainer(name='id2_service', status='stopped'),
                                                    MockedContainer(name='id3_not_service', status='running'))

        expected_result = b'{"messageType": "SERVICES_STATUS", ' \
                          b'"body": {"statuses": [{"serviceId": "Id1", "status": "UP"}, {"serviceId": "id-2", "status": "DOWN"}]}}', \
                          ["id-2"]

        result = check_service_statuses()

        self.assertEqual(result, expected_result)

    @mock.patch('docker.from_env')
    @mock.patch('agent.commands.service_status.get_services_id_list')
    def test_check_service_statuses__when_empty_services_list(self, mock_id_list, mock_containers):
        mock_id_list.return_value = []
        mock_containers.return_value = MockedClient(MockedContainer(name='id_name', status='running'))

        expected_result = b'{"messageType": "SERVICES_STATUS", "body": {"statuses": []}}', \
                          []

        result = check_service_statuses()

        self.assertEqual(result, expected_result)

    @mock.patch('docker.from_env')
    @mock.patch('agent.commands.service_status.get_services_id_list')
    def test_check_service_statuses__when_containers_does_not_exist(self, mock_id_list, mock_containers):
        mock_id_list.return_value = ['Id', 'id2']
        mock_containers.return_value = MockedClient()

        expected_result = b'{"messageType": "SERVICES_STATUS", "body": {"statuses": []}}',\
                          []

        result = check_service_statuses()

        self.assertEqual(result, expected_result)

    @mock.patch('docker.from_env')
    @mock.patch('agent.commands.service_status.get_services_id_list')
    def test_check_service_statuses__when_one_of_service_containers_is_down(self, mock_id_list, mock_containers):
        mock_id_list.return_value = ['Id1', 'id2']
        mock_containers.return_value = MockedClient(MockedContainer(name='id1_database', status='running'),
                                                    MockedContainer(name='id1_service', status='stopped'),
                                                    MockedContainer(name='id2_service', status='running'))

        expected_result = b'{"messageType": "SERVICES_STATUS", ' \
                          b'"body": {"statuses": [{"serviceId": "Id1", "status": "DOWN"}, {"serviceId": "id2", "status": "UP"}]}}',\
                          ["Id1"]

        result = check_service_statuses()

        self.assertEqual(result, expected_result)

    @mock.patch('docker.from_env')
    @mock.patch('agent.commands.service_status.get_services_id_list')
    def test_check_service_statuses__when_service_has_two_containers(self, mock_id_list, mock_containers):
        mock_id_list.return_value = ['Id1', 'id2']
        mock_containers.return_value = MockedClient(MockedContainer(name='id1_database', status='running'),
                                                    MockedContainer(name='id1_service', status='running'),
                                                    MockedContainer(name='id2_service', status='running'))

        expected_result = b'{"messageType": "SERVICES_STATUS", ' \
                          b'"body": {"statuses": [{"serviceId": "Id1", "status": "UP"}, {"serviceId": "id2", "status": "UP"}]}}',\
                          []

        result = check_service_statuses()

        self.assertEqual(result, expected_result)
