from unittest import mock
from unittest.case import TestCase

from agent.commands.smart_card_reader import find_smart_card_reader_address
from agent.exceptions.agent_error import AgentError


class TestUSBDeviceFinder(TestCase):

    @mock.patch('agent.commands.smart_card_reader._get_reader_usb_details')
    def test_find_smart_card_reader_address(self, mock_lsusb):
        mock_lsusb.return_value = 'Bus 001 Device 003: ID 04e6:5724 SCM Microsystems, Inc.\n' \
                                  '      bInterfaceClass        11 Chip/SmartCard\n'

        expected_path = '/dev/bus/usb/001/003'

        result = find_smart_card_reader_address()

        self.assertEqual(result, expected_path)

    @mock.patch('agent.commands.smart_card_reader._parse_reader_address')
    @mock.patch('os.getenv')
    @mock.patch('agent.commands.smart_card_reader._get_reader_usb_details')
    def test_find_smart_card_reader_address__when_device_not_found(self, mock_lsusb, mock_env, mock_parse):
        mock_lsusb.side_effect = AgentError(None, 'Error')
        mock_env.return_value = 'SmartCard Reader'

        with self.assertRaises(AgentError) as e:
            find_smart_card_reader_address()

        mock_parse.assert_not_called()
