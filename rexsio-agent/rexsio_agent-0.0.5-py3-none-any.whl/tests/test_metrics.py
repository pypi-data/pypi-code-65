from socket import AF_INET, AF_INET6
from unittest import mock
from unittest.case import TestCase

from agent.commands.metrics import read_metrics


class MockedSnicaddr:
    def __init__(self, address, family):
        self.address = address
        self.family = family


class TestMetrics(TestCase):

    @mock.patch('psutil.net_if_addrs')
    def test_read_ip_address(self, mock_net_addresses):
        lo_list = [MockedSnicaddr(address='127.0.0.1', family=AF_INET),
                   MockedSnicaddr(address='::1', family=AF_INET6)]
        eth_list = [MockedSnicaddr(address='192.168.1.11', family=AF_INET),
                    MockedSnicaddr(address='fe81::6ac6:ca13:c330:1fae%enp0s31f6', family=AF_INET6)]
        mock_net_addresses.return_value = dict(lo=lo_list, enp0s31f6=eth_list)

        expected_result = b'{"messageType": "NODE_METRICS", ' \
                          b'"body": {"ip": "192.168.1.11"}}'

        result = read_metrics()

        self.assertEqual(result, expected_result)

    @mock.patch('psutil.net_if_addrs')
    def test_read_ip_address__when_no_ethernet_interface(self, mock_net_addresses):
        lo_list = [MockedSnicaddr(address='127.0.0.1', family=AF_INET),
                   MockedSnicaddr(address='::1', family=AF_INET6)]
        mock_net_addresses.return_value = dict(lo=lo_list)

        expected_result = b'{"messageType": "NODE_METRICS", ' \
                          b'"body": {"ip": null}}'

        result = read_metrics()

        self.assertEqual(result, expected_result)

    @mock.patch('psutil.net_if_addrs')
    def test_read_ip_address__when_no_ip_found(self, mock_net_addresses):
        lo_list = [MockedSnicaddr(address='::1', family=AF_INET6)]
        eth_list = [MockedSnicaddr(address='fe81::6ac6:ca13:c330:1fae%enp0s31f6', family=AF_INET6)]
        mock_net_addresses.return_value = dict(lo=lo_list, enp0s31f6=eth_list)

        expected_result = b'{"messageType": "NODE_METRICS", ' \
                          b'"body": {"ip": null}}'

        result = read_metrics()

        self.assertEqual(result, expected_result)

