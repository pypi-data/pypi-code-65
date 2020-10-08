# The intention is to make the test names descriptive enough to not need any docstrings for most of them
#pylint: disable=missing-docstring
# It seems better to have all tests for one module in the same file than to split across multiple files,
# so accepting many public methods and many lines makes sense
#pylint: disable=too-many-lines
#pylint: disable=too-many-public-methods
"""
pydebuggerconfig CLI unit tests
"""
import unittest
import io
from copy import deepcopy
from argparse import Namespace
from mock import create_autospec
from mock import patch

from pydebuggerconfig.pydebuggerconfig_main import pydebuggerconfig
from pydebuggerconfig.pydebuggerconfig_errors import PydebuggerconfigToolConnectionError, PydebuggerconfigError
from pydebuggerconfig.backend import Backend

DEFAULT_ARGS = Namespace(
    action='show',
    board=None,
    debug=False,
    device=None,
    factory=False,
    register=None,
    preserve=None,
    release_info=False,
    config_serialnumber=None,
    verbose=False,
    version=False,
    serialnumber='')


class TestPydebuggerconfigCLI(unittest.TestCase):
    """pydebuggerconfig CLI unit tests

    Tests the CLI by calling pydebuggerconfig_main.pydebuggerconfig with Namespace containing arguments. These tests
    only test the CLI layer, the pydebuggerconfig backend layer is mocked out.
    """
    def setUp(self):
        # Mock out stdout to be able to control (and possibly check) the output
        self.mock_stdout_patch = patch('sys.stdout', new_callable=io.StringIO)
        self.addCleanup(self.mock_stdout_patch.stop)
        self.mock_stdout = self.mock_stdout_patch.start()

        mock_backend_patch = patch("pydebuggerconfig.pydebuggerconfig_main.Backend", autospec=True)
        self.addCleanup(mock_backend_patch.stop)
        self.mock_backend = mock_backend_patch.start()

        self.mock_backend_instance = create_autospec(Backend)
        self.mock_backend.return_value = self.mock_backend_instance

    def test_generate_hex(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = "dummy_boardfile.xml"
        arguments.device = "dummy_devicefile.xml"
        arguments.action = 'generate-hex'

        self.mock_backend_instance.generate_hex.return_value = "generated_dummy.hex"

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend_instance.generate_hex.assert_called_with(arguments.board, arguments.device)

    def test_show_both_board_and_device(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = "dummy_boardfile.xml"
        arguments.device = "dummy_devicefile.xml"
        arguments.action = 'show'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend_instance.get_board_config_as_string.assert_called_with(arguments.board)
        self.mock_backend_instance.get_device_config_as_string.assert_called_with(arguments.device)

    def test_show_board(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = "dummy_boardfile.xml"
        arguments.device = None
        arguments.action = 'show'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend_instance.get_board_config_as_string.assert_called_with(arguments.board)
        self.mock_backend_instance.get_device_config_as_string.assert_not_called()

    def test_show_none(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = None
        arguments.device = None
        arguments.action = 'show'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend_instance.get_board_config_as_string.assert_not_called()
        self.mock_backend_instance.get_device_config_as_string.assert_not_called()

    def test_read_user(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.action = 'read'
        arguments.serialnumber = "MY_USB_DEVICE0123456"

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with(arguments.serialnumber)
        self.mock_backend_instance.read_board_config_as_string.assert_called_with(factory_config=False)
        self.mock_backend_instance.read_device_config_as_string.assert_called_with()

    def test_read_factory(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.action = 'read'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with('')
        self.mock_backend_instance.read_board_config_as_string.assert_called_with(factory_config=True)
        self.mock_backend_instance.read_device_config_as_string.assert_called_with()

    def test_read_when_tool_connection_fails_for_board_config_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = False
        arguments.action = 'read'

        self.mock_backend_instance.read_board_config_as_string.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_read_when_tool_connection_fails_for_device_config_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = False
        arguments.action = 'read'

        self.mock_backend_instance.read_device_config_as_string.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_write_board_config(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.board = "dummy_boardfile.xml"
        arguments.device = None
        arguments.preserve = ['PRESERVE1', 'PRESERVE2']
        arguments.action = 'write'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with('')
        self.mock_backend_instance.write_board_config.assert_called_with(board_xml_file=arguments.board,
                                                                         factory_config=arguments.factory,
                                                                         serialnumber=arguments.config_serialnumber,
                                                                         preserve=arguments.preserve)
        self.mock_backend_instance.write_device_config.assert_not_called()

    def test_write_board_config_when_tool_connection_fails_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = "dummy_boardfile.xml"
        arguments.device = None
        arguments.action = 'write'

        self.mock_backend_instance.write_board_config.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_write_board_config_when_backend_raises_pydebuggerconfigerror_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = "dummy_boardfile.xml"
        arguments.device = None
        arguments.action = 'write'

        self.mock_backend_instance.write_board_config.side_effect = \
            PydebuggerconfigError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_write_device_config(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = None
        arguments.device = "dummy_devicefile.xml"
        arguments.action = 'write'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with('')
        self.mock_backend_instance.write_board_config.assert_not_called()
        self.mock_backend_instance.write_device_config.assert_called_with(device_xml_file=arguments.device)

    def test_write_device_config_when_tool_connection_fails_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = None
        arguments.device = "dummy_devicefile.xml"
        arguments.action = 'write'

        self.mock_backend_instance.write_device_config.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_write_board_and_device_config(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.board = "dummy_boardfile.xml"
        arguments.device = "dummy_devicefile.xml"
        arguments.config_serialnumber = "01234567890123456789"
        arguments.serialnumber = "MY_USB_DEVICE0123456"
        arguments.preserve = ['PRESERVE1', 'PRESERVE2']
        arguments.action = 'write'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with(arguments.serialnumber)
        self.mock_backend_instance.write_board_config.assert_called_with(board_xml_file=arguments.board,
                                                                         factory_config=arguments.factory,
                                                                         serialnumber=arguments.config_serialnumber,
                                                                         preserve=arguments.preserve)
        self.mock_backend_instance.write_device_config.assert_called_with(device_xml_file=arguments.device)

    def test_verify_board_and_device(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.board = "dummy_boardfile.xml"
        arguments.device = "dummy_devicefile.xml"
        arguments.serialnumber = "MY_USB_DEVICE0123456"
        arguments.action = 'verify'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with(arguments.serialnumber)
        self.mock_backend_instance.read_board_config_as_string.assert_called_with(factory_config=True)
        self.mock_backend_instance.read_device_config_as_string.assert_called_with()
        self.mock_backend_instance.get_board_config_as_string.assert_called_with(arguments.board)
        self.mock_backend_instance.get_device_config_as_string.assert_called_with(arguments.device)

    def test_verify_board_only(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = False
        arguments.board = "dummy_boardfile.xml"
        arguments.device = None
        arguments.action = 'verify'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with('')
        self.mock_backend_instance.read_board_config_as_string.assert_called_with(factory_config=False)
        self.mock_backend_instance.read_device_config_as_string.assert_not_called()
        self.mock_backend_instance.get_board_config_as_string.assert_called_with(board_xml_file=arguments.board)
        self.mock_backend_instance.get_device_config_as_string.assert_not_called()

    def test_verify_device_only(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.board = None
        arguments.device = "dummy_devicefile.xml"
        arguments.action = 'verify'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with('')
        self.mock_backend_instance.read_board_config_as_string.assert_not_called()
        self.mock_backend_instance.read_device_config_as_string.assert_called_with()
        self.mock_backend_instance.get_board_config_as_string.assert_not_called()
        self.mock_backend_instance.get_device_config_as_string.assert_called_with(arguments.device)

    def test_verify_neither_board_nor_device(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.board = None
        arguments.device = None
        arguments.action = 'verify'

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend_instance.read_board_config_as_string.assert_not_called()
        self.mock_backend_instance.read_device_config_as_string.assert_not_called()
        self.mock_backend_instance.get_board_config_as_string.assert_not_called()
        self.mock_backend_instance.get_device_config_as_string.assert_not_called()

    def test_verify_board_when_tool_connection_fails_return_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = "dummy_boardfile.xml"
        arguments.device = None
        arguments.action = 'verify'

        self.mock_backend_instance.read_board_config_as_string.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_verify_device_when_tool_connection_fails_return_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.board = None
        arguments.device = "dummy_devicefile.xml"
        arguments.action = 'verify'

        self.mock_backend_instance.read_device_config_as_string.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_replace(self):
        new_serial = "MY_NEW_SERIAL0123456"
        new_kit_name = "MY_NEW_KIT_NAME"
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.serialnumber = "MY_USB_DEVICE0123456"
        arguments.action = 'replace'
        arguments.register = []
        registers_dict = {'SERNUM':new_serial, 'KITNAME':new_kit_name}
        for register in registers_dict:
            arguments.register.append('{}={}'.format(register, registers_dict[register]))

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with(arguments.serialnumber)
        self.mock_backend_instance.replace.assert_called_with(registers_dict=registers_dict,
                                                              factory_config=arguments.factory)

    def test_replace_when_backend_raises_pydebuggerconfigerror_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.factory = True
        arguments.action = 'replace'
        arguments.register = ['UNKNOWN_register=1']

        self.mock_backend_instance.replace.side_effect = PydebuggerconfigError("Exception injected into Backend mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_replace_when_tool_connection_fails_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.action = 'replace'
        arguments.register = ['SERNUM=01234567890123456789']

        self.mock_backend_instance.replace.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_restore(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.serialnumber = "MY_USB_DEVICE0123456"
        arguments.action = "restore"

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with(arguments.serialnumber)
        self.mock_backend_instance.restore_board_config.assert_called_with()

    def test_restore_when_tool_connection_fails_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.action = 'restore'

        self.mock_backend_instance.restore_board_config.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)

    def test_version_update_newer_version_exists(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.serialnumber = "MY_USB_DEVICE0123456"
        arguments.action = "version-update"

        self.mock_backend_instance.update_board_config_version.return_value = (True, '1.1.1')

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with(arguments.serialnumber)
        self.mock_backend_instance.update_board_config_version.assert_called_with()

    def test_version_update_already_up_to_date(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.action = "version-update"

        self.mock_backend_instance.update_board_config_version.return_value = (False, '1.1.1')

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 0)
        self.mock_backend.assert_called_with('')
        self.mock_backend_instance.update_board_config_version.assert_called_with()

    def test_version_update_when_tool_connection_fails_returns_1(self):
        arguments = deepcopy(DEFAULT_ARGS)
        arguments.action = 'version-update'

        self.mock_backend_instance.update_board_config_version.side_effect = \
            PydebuggerconfigToolConnectionError("Exception injected into Backend Mock")

        returncode = pydebuggerconfig(arguments)

        self.assertEqual(returncode, 1)
