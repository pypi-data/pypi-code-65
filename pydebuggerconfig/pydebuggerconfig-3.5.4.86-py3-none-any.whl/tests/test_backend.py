# The intention is to make the test names descriptive enough to not need any docstrings for most of them
#pylint: disable=missing-docstring
# It seems better to have all tests for one module in the same file than to split across multiple files,
# so accepting many public methods and many lines makes sense
#pylint: disable=too-many-lines
#pylint: disable=too-many-public-methods
"""
pydebuggerconfig backend API tests

These tests validates the API used by external front-ends/scripts
"""
import unittest
import os.path
import copy
import datetime
import glob
from distutils.version import LooseVersion
from packaging import version
from intelhex import IntelHex
from mock import patch, MagicMock, call

from pydebuggerconfig.backend import Backend
from pydebuggerconfig.pydebuggerconfig_errors import PydebuggerconfigError, PydebuggerconfigToolConnectionError
from pydebuggerconfig.tests.dummy_data import BOARD_CONFIG_TEST_DATA, DEVICE_CONFIG_TEST_DATA

class TestBackend(unittest.TestCase):
    """
    pydebuggerconfig backend API tests
    """
    DEVICE_CONFIG_ADDRESS = 0x3F100
    USER_CONFIG_START_ADDRESS = 0x3FC00
    FACTORY_CONFIG_START_ADDRESS = 0x3FE00
    CONFIG_END_ADDRESS = 0x40000
    CONFIG_DEVNAME_OFFSET = 0xC0
    CONFIG_PROGBASE_OFFSET = 0x28
    CONFIG_FLASHSIZE_OFFSET = 0x3A
    CONFIG_DATE_OFFSET = 0xF8
    CONFIG_SERNUM_OFFSET = 0xE0
    CONFIG_KITNAME_OFFSET = 0x48
    CONFIG_DEVNAME_OFFSET = 0xC0
    CONFIG_MAJOR_VERSION_OFFSET = 0x00
    CONFIG_MINOR_VERSION_OFFSET = 0x01
    CONFIG_BUILD_NUMBER_OFFSET = 0x02

    BOARD_CONFIG_FILE = "ATmega4809-CNANO.xml"
    BOARD_CONFIG_FILE_PATH = os.path.join("board-configs", BOARD_CONFIG_FILE)
    DEVICE_CONFIG_FILE = "ATmega4809-device-blob.xml"
    DEVICE_CONFIG_FILE_PATH = os.path.join("device-configs", DEVICE_CONFIG_FILE)
    USB_SERIAL_SUBSTRING = "0123456789"

    def setUp(self):
        self.backend = Backend(self.USB_SERIAL_SUBSTRING)

    def _check_empty_config(self, start_address, end_address, ihex_obj):
        """Check that there is no data in the given config section of the hexfile

        :param start_address: First location in section to check
        :type start_address: int
        :param end_address: First location to not check (i.e. last location to check is end_address-1)
        :type end_address: int
        :param ihex_obj: IntelHex object representing the hexfile
        :type ihex_obj: class: intelhex.IntelHex
        """
        for index in range(start_address, end_address-start_address):
            self.assertEqual(ihex_obj[index],
                             0xFF,
                             "Found unexpected config data @0x{:X}".format(self.DEVICE_CONFIG_ADDRESS+index))


    def _check_devicename_hexfile(self, devicename, ihex_obj):
        """Check that the device name in the hex file is correct

        Both the factory config and the user config is checked
        :param devicename: Expected device name
        :type devicename: str
        :param ihex_obj: IntelHex object representing the hexfile
        :type ihex_obj: class: intelhex.IntelHex
        """
        factory_config_devname_address = self.FACTORY_CONFIG_START_ADDRESS + self.CONFIG_DEVNAME_OFFSET
        user_config_devname_address = self.USER_CONFIG_START_ADDRESS + self.CONFIG_DEVNAME_OFFSET

        # Check device name in user config
        devname_user_hex = ''
        for index in range(len(devicename)):
            devname_user_hex += chr(ihex_obj[user_config_devname_address+index])

        self.assertIn(devicename, devname_user_hex, "Incorrect device name in User config part of hexfile")

        # Check device name in factory config
        devname_factory_hex = ''
        for index in range(len(devicename)):
            devname_factory_hex += chr(ihex_obj[factory_config_devname_address+index])

        self.assertIn(devicename, devname_factory_hex, "Incorrect device name in Factory config part of hexfile")

    def _check_progbase_hexfile(self, progbase, ihex_obj):
        """Check that the progbase value in the hex file is correct

        :param progbase: Expected progbase value (16-bits)
        :type progbase: int
        :param ihex_obj: IntelHex object representing the hexfile
        :type ihex_obj: class: intelhex.IntelHex
        """
        progbase_address = self.DEVICE_CONFIG_ADDRESS + self.CONFIG_PROGBASE_OFFSET
        progbase_hex = (ihex_obj[progbase_address + 1] << 8) + (ihex_obj[progbase_address] & 0x00FF)
        self.assertEqual(progbase_hex, progbase, "Incorrect progbase found in hex file")

    def _check_flashsize_hexfile(self, flashsize, ihex_obj):
        """Check that the flashsize value in the hex file is correct

        :param flashsize: Expected flashsize value (16-bits)
        :type flashsize: int
        :param ihex_obj: IntelHex object representing the hexfile
        :type ihex_obj: class: intelhex.IntelHex
        """
        flashsize_address = self.DEVICE_CONFIG_ADDRESS + self.CONFIG_FLASHSIZE_OFFSET
        flashsize_hex = (ihex_obj[flashsize_address + 1] << 8) + (ihex_obj[flashsize_address] & 0x00FF)
        self.assertEqual(flashsize_hex, flashsize, "Incorrect flash size found in hex file")

    @staticmethod
    def _update_test_data_with_string(test_data, offset, value):
        """Update test data with provided values starting at provided offset

        :param test_data: List of byte values
        :type test_data: list[byte]
        :param offset: Offset to start updating data at
        :type offset: int
        :param value: String to put into the test data
        :type value: str
        """
        for byte in value:
            test_data[offset] = ord(byte)
            offset += 1

    @staticmethod
    def _get_board_config_test_data():
        # It is important to take a copy of the test data to avoid that the original test data is altered by the
        # code being tested since parameters are normally passed as pointers
        return copy.deepcopy(BOARD_CONFIG_TEST_DATA)

    @staticmethod
    def _get_device_config_test_data():
        # It is important to take a copy of the test data to avoid that the original test data is altered by the
        # code being tested since parameters are normally passed as pointers
        return copy.deepcopy(DEVICE_CONFIG_TEST_DATA)

    def _get_board_config_test_data_with_updated_date(self, serialnumber=None):
        """Returns board config data with DATE set to today

        :param serialnumber: Serial number (20 ascii characters) to inject into the test data, defaults to None.  If
            set to None the serial number will not be updated.
        :type serialnumber: str
        """
        # Updating board config with todays date as Manufacturing date (DATE register)
        date = datetime.datetime.now().strftime("%Y%m%d")
        board_config_test_data_updated_date = self._get_board_config_test_data()
        self._update_test_data_with_string(board_config_test_data_updated_date, self.CONFIG_DATE_OFFSET, date)
        if serialnumber is not None:
            self._update_test_data_with_string(board_config_test_data_updated_date,
                                               self.CONFIG_SERNUM_OFFSET, serialnumber)

        return board_config_test_data_updated_date

    @staticmethod
    def _find_latest_board_spec_version(major_version):
        """Find latest board specification version with given major version

        Example:
            These versions exists: ['1.2.0', '1.3.5', '2.1.2', '3.2.4']
            _find_latest_board_spec_version(1) returns '1.3.5'
            _find_latest_board_spec_version(3) returns '3.2.4'
        :param major_version: Major specification version
        :type major_version: str
        :return: Latest board specification available with a major version matching the major_version parameter
        :rtype: str
        """
        # Find latest version in the specs and write it to the expected data
        specification_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "config-specification")
        specification_name = "board_config_defines"
        ext = 'xml'

        files = glob.glob('{}//{}-{}*.{}'.format(specification_folder, specification_name, major_version, ext))

        # Parse all candidates to find the latest version
        latest = "{}.0.0".format(major_version)
        for specfile in files:
            # Split out the version
            spec_version = specfile.split('{}-'.format(specification_name))[1].split('.{}'.format(ext))[0]
            # And the major part thereof
            spec_major = spec_version.split('.')[0]
            # Only if major matches will this be a candidate
            if int(spec_major) == int(major_version):
                # And only if its an upgrade
                if version.parse(spec_version) > version.parse(latest):
                    latest = spec_version

        return latest

    def _mock_hid_transport(self):
        mock_hid_transport_patch = patch("pydebuggerconfig.backend.hid_transport")
        self.addCleanup(mock_hid_transport_patch.stop)
        mock_hid_transport = mock_hid_transport_patch.start()

        mock_hid_transport_instance = MagicMock()
        mock_hid_transport.return_value = mock_hid_transport_instance

        return mock_hid_transport_instance

    def test_get_api_version_returns_major_version_1_or_higher(self):
        """Simple sanity test of the get_api_version method"""
        api_version_read = self.backend.get_api_version()

        self.assertGreaterEqual(LooseVersion(api_version_read), LooseVersion('1.0'))

    def test_get_board_config_as_string(self):
        """Sanity test of the get_board_config_as_string method

        Just picking a board file and doing some sanity checking of the returned string
        """
        config_string = self.backend.get_board_config_as_string(self.BOARD_CONFIG_FILE_PATH)

        self.assertIsInstance(config_string, str)
        self.assertIn("Register DEVNAME", config_string)
        self.assertIn('"ATmega4809" # Target name', config_string)

    def test_get_board_config_as_string_when_file_does_not_exist_raises_ioerror(self):
        with self.assertRaises(IOError):
            self.backend.get_board_config_as_string("non-existing.xml")

    def test_get_device_config_as_string(self):
        """Sanity test of the get_device_config_as_string method

        Just picking a device file and doing some sanity checking of the returned string
        """
        config_string = self.backend.get_device_config_as_string(self.DEVICE_CONFIG_FILE_PATH)

        self.assertIsInstance(config_string, str)
        self.assertIn("Register INTERFACE_TYPE:", config_string)
        self.assertIn('UPDI_TINYX_API', config_string)

    def test_get_device_config_as_string_when_file_does_not_exist_raises_ioerror(self):
        with self.assertRaises(IOError):
            self.backend.get_device_config_as_string("non-existing.xml")

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    def test_read_board_config_as_string_user_config(self, mock_read_config_block):
        mock_hid_transport = self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        config_string = self.backend.read_board_config_as_string()

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        mock_read_config_block.assert_called_with(False)
        self.assertIsInstance(config_string, str)
        self.assertIn("Register DEVNAME", config_string)
        self.assertIn('"ATmega4809" # Target name', config_string)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    def test_read_board_config_as_string_factory_config(self, mock_read_config_block):
        mock_hid_transport = self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        config_string = self.backend.read_board_config_as_string(factory_config=True)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        mock_read_config_block.assert_called_with(True)
        self.assertIsInstance(config_string, str)
        self.assertIn("Register DEVNAME", config_string)
        self.assertIn('"ATmega4809" # Target name', config_string)

    def test_read_board_config_as_string_raises_when_hid_transport_connect_returns_false(self):
        """Test that when no tool or too many tools are connected a PydebuggerconfigToolConnectionError is raised

        It is sufficient to test this behavior on one of the methods using the BoardConfig object as the tool
        connection is handled by the board_config_manager
        """
        mock_hid_transport = self._mock_hid_transport()
        mock_hid_transport.connect.return_value = False

        with self.assertRaises(PydebuggerconfigToolConnectionError):
            self.backend.read_board_config_as_string()

    def test_read_board_config_as_string_raises_when_hid_transport_raises_ioerror(self):
        """Test that when the tool connection fails a PydebuggerconfigToolConnectionError is raised

        It is sufficient to test this behavior on one of the methods using the BoardConfig object as the tool
        connection is handled by the board_config_manager
        """
        mock_hid_transport = self._mock_hid_transport()
        mock_hid_transport.connect.side_effect = IOError("Exception injected into HID transport Mock")

        with self.assertRaises(PydebuggerconfigToolConnectionError):
            self.backend.read_board_config_as_string()

    def test_read_device_config_as_string_raises_when_hid_transport_connect_returns_false(self):
        """Test that when no tool or too many tools are connected a PydebuggerconfigToolConnectionError is raised

        It is sufficient to test this behavior on one of the methods using the DeviceConfig object as the tool
        connection is handled by the device_config_manager
        """
        mock_hid_transport = self._mock_hid_transport()
        mock_hid_transport.connect.return_value = False

        with self.assertRaises(PydebuggerconfigToolConnectionError):
            self.backend.read_device_config_as_string()

    def test_read_device_config_as_string_raises_when_hid_transport_raises_ioerror(self):
        """Test that when the tool connection fails a PydebuggerconfigToolConnectionError is raised

        It is sufficient to test this behavior on one of the methods using the DeviceConfig object as the tool
        connection is handled by the device_config_manager
        """
        mock_hid_transport = self._mock_hid_transport()
        mock_hid_transport.connect.side_effect = IOError("Exception injected into HID transport Mock")

        with self.assertRaises(PydebuggerconfigToolConnectionError):
            self.backend.read_device_config_as_string()

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_device_data_block")
    def test_read_device_config_as_string(self, mock_read_device_data_block):
        mock_hid_transport = self._mock_hid_transport()
        mock_read_device_data_block.return_value = DEVICE_CONFIG_TEST_DATA

        config_string = self.backend.read_device_config_as_string()

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        # Just some sanity checks of the returned string representation of the received config data
        self.assertIsInstance(config_string, str)
        self.assertIn("Register INTERFACE_TYPE:", config_string)
        self.assertIn('UPDI_TINYX_API', config_string)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_write_board_config_default_params(self, mock_write_config_block):
        mock_hid_transport = self._mock_hid_transport()

        config_string = self.backend.write_board_config(self.BOARD_CONFIG_FILE_PATH)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        board_config_test_data = self._get_board_config_test_data_with_updated_date()
        mock_write_config_block.assert_called_with(board_config_test_data, factory=False)
        # Just some sanity checks of the returned string representation of the written board config data
        self.assertIsInstance(config_string, str)
        self.assertIn("Register DEVNAME", config_string)
        self.assertIn('"ATmega4809" # Target name', config_string)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_write_board_config_raises_when_preserve_contains_invalid_register(self,
                                                                               mock_write_config_block,
                                                                               mock_read_config_block):
        # pylint: disable=unused-argument
        self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        with self.assertRaises(PydebuggerconfigError):
            self.backend.write_board_config(self.BOARD_CONFIG_FILE_PATH, preserve=['UNKNOWN'])

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_write_board_config_set_serial(self, mock_write_config_block):
        new_serial = "NEWSERIAL01234567890"
        mock_hid_transport = self._mock_hid_transport()

        config_string = self.backend.write_board_config(self.BOARD_CONFIG_FILE_PATH, serialnumber=new_serial)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        board_config_test_data = self._get_board_config_test_data_with_updated_date(serialnumber=new_serial)
        mock_write_config_block.assert_called_with(board_config_test_data, factory=False)
        # Just a sanity check of the returned string representation of the written board config data
        self.assertIsInstance(config_string, str)
        self.assertIn("Register DEVNAME", config_string)
        self.assertIn('"ATmega4809" # Target name', config_string)
        self.assertIn(new_serial, config_string)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_write_board_config_factory(self, mock_write_config_block):
        mock_hid_transport = self._mock_hid_transport()

        self.backend.write_board_config(self.BOARD_CONFIG_FILE_PATH, factory_config=True)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        board_config_test_data = self._get_board_config_test_data_with_updated_date()
        # When factory_config parameter is True both the factory and the user config should be written
        mock_write_config_block.assert_has_calls([call(board_config_test_data, factory=True),
                                                  call(board_config_test_data, factory=False)],
                                                 any_order=True)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_write_board_config_preserve_kitname_sernum(self, mock_write_config_block, mock_read_config_block):
        # Of simplicity the kitname is given as exactly 60 characters which is the size of the KITNAME register
        old_kitname = "THIS IS THE OLD KIT NAME WHICH SHOULD BE PRESERVED 60 CARAC"
        # Serial numbers are always 20 characters long
        old_sernum = "OLDSERIAL_PRESERVED1"
        # Of simplicity the devname is given as exactly 32 characters which is the size of the DEVNAME register
        old_devname = "OLD DEVICE NAME TO OVERWRITE 111"

        mock_hid_transport = self._mock_hid_transport()

        # Prepare config data to return when reading from the board
        test_data_from_board = self._get_board_config_test_data()
        # Modify the test data to be read from the board to check that the correct registers are preserved
        self._update_test_data_with_string(test_data_from_board, self.CONFIG_KITNAME_OFFSET, old_kitname)
        self._update_test_data_with_string(test_data_from_board, self.CONFIG_SERNUM_OFFSET, old_sernum)
        self._update_test_data_with_string(test_data_from_board, self.CONFIG_DEVNAME_OFFSET, old_devname)

        mock_read_config_block.return_value = test_data_from_board

        config_string = self.backend.write_board_config(self.BOARD_CONFIG_FILE_PATH, preserve=['SERNUM', 'KITNAME'])

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        # Prepare the config data to be used to verify the written data
        board_config_expected_data = self._get_board_config_test_data_with_updated_date()
        # Put in the config register values that should be preserved
        self._update_test_data_with_string(board_config_expected_data, self.CONFIG_KITNAME_OFFSET, old_kitname)
        self._update_test_data_with_string(board_config_expected_data, self.CONFIG_SERNUM_OFFSET, old_sernum)
        mock_write_config_block.assert_called_with(board_config_expected_data, factory=False)
        mock_read_config_block.assert_called_with(False)
        # Just a sanity check of the returned string representation of the written board config data
        self.assertIsInstance(config_string, str)
        self.assertIn("Register DEVNAME", config_string)
        self.assertIn('"ATmega4809" # Target name', config_string)
        self.assertIn(old_sernum, config_string)
        self.assertIn(old_kitname, config_string)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_device_data_block")
    def test_write_device_config(self, mock_write_device_data_block):
        mock_hid_transport = self._mock_hid_transport()

        config_string = self.backend.write_device_config(self.DEVICE_CONFIG_FILE_PATH)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        mock_write_device_data_block.assert_called_with(DEVICE_CONFIG_TEST_DATA)
        # Just a sanity check of the returned string representation of the written device config data
        self.assertIsInstance(config_string, str)
        self.assertIn("Register INTERFACE_TYPE:", config_string)
        self.assertIn('UPDI_TINYX_API', config_string)


    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_replace_kitname_sernum_user_config(self, mock_write_config_block, mock_read_config_block):
        # Of simplicity the kitname is given as exactly 60 characters which is the size of the KITNAME register
        kitname = "THIS IS THE NEW KIT NAME WHICH SHOULD BE WRITTEN 60 CAR 123"
        # Serial numbers are always 20 characters long
        sernum = "NEWSERIAL_TO_WRITE_1"
        replace_dict = {"KITNAME": kitname, "SERNUM": sernum}

        mock_hid_transport = self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        self.backend.replace(replace_dict, factory_config=False)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()

        # Prepare the config data to be used to verify the written data
        board_config_expected_data = self._get_board_config_test_data_with_updated_date()
        # Put in the config register values that should have been updated
        self._update_test_data_with_string(board_config_expected_data, self.CONFIG_KITNAME_OFFSET, kitname)
        self._update_test_data_with_string(board_config_expected_data, self.CONFIG_SERNUM_OFFSET, sernum)
        mock_write_config_block.assert_called_with(board_config_expected_data, factory=False)
        mock_read_config_block.assert_called_with(False)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_replace_kitname_sernum_factory_config(self, mock_write_config_block, mock_read_config_block):
        # Of simplicity the kitname is given as exactly 60 characters which is the size of the KITNAME register
        kitname = "THIS IS THE NEW KIT NAME WHICH SHOULD BE WRITTEN 60 CAR 456"
        # Serial numbers are always 20 characters long
        sernum = "NEWSERIAL_TO_WRITE_2"
        replace_dict = {"KITNAME": kitname, "SERNUM": sernum}

        mock_hid_transport = self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        self.backend.replace(replace_dict, factory_config=True)

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()

        # Prepare the config data to be used to verify the written data
        board_config_expected_data = self._get_board_config_test_data_with_updated_date()
        # Put in the config register values that should have been updated
        self._update_test_data_with_string(board_config_expected_data, self.CONFIG_KITNAME_OFFSET, kitname)
        self._update_test_data_with_string(board_config_expected_data, self.CONFIG_SERNUM_OFFSET, sernum)
        mock_write_config_block.assert_called_with(board_config_expected_data, factory=True)
        mock_read_config_block.assert_called_with(True)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_restore_board_config(self, mock_write_config_block, mock_read_config_block):
        mock_hid_transport = self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        self.backend.restore_board_config()

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        board_config_expected_data = self._get_board_config_test_data_with_updated_date()
        mock_write_config_block.assert_called_with(board_config_expected_data, factory=False)
        mock_read_config_block.assert_called_with(True)

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_update_board_config_version_when_newer_version_exists(self,
                                                                   mock_write_config_block,
                                                                   mock_read_config_block):
        mock_hid_transport = self._mock_hid_transport()
        mock_read_config_block.return_value = self._get_board_config_test_data()

        (updated, current_version) = self.backend.update_board_config_version()

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()

        board_config_expected_data = self._get_board_config_test_data_with_updated_date()
        # Find latest version in the specs and write it to the expected data
        new_version = self._find_latest_board_spec_version(board_config_expected_data[self.CONFIG_MAJOR_VERSION_OFFSET])
        new_version_list = new_version.split(".")
        board_config_expected_data = self._get_board_config_test_data_with_updated_date()
        board_config_expected_data[self.CONFIG_MINOR_VERSION_OFFSET] = int(new_version_list[1])
        board_config_expected_data[self.CONFIG_BUILD_NUMBER_OFFSET] = int(new_version_list[2])

        mock_write_config_block.assert_called_with(board_config_expected_data, factory=False)
        mock_read_config_block.assert_called_with(False)

        self.assertTrue(updated, msg="Version update did not happen (returned False)")
        self.assertEqual(current_version, new_version, msg="Unexpected version reported after update")

    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.read_config_block")
    @patch("pydebuggerconfig.boardconfig.configprotocol.ConfigProtocol.write_config_block")
    def test_update_board_config_version_when_already_up_to_date(self, mock_write_config_block, mock_read_config_block):
        mock_hid_transport = self._mock_hid_transport()
        test_data = self._get_board_config_test_data()
        # Find latest version in the specs and write it to the test data so that no update will be needed
        new_version = self._find_latest_board_spec_version(test_data[self.CONFIG_MAJOR_VERSION_OFFSET])
        new_version_list = new_version.split(".")
        test_data[self.CONFIG_MINOR_VERSION_OFFSET] = int(new_version_list[1])
        test_data[self.CONFIG_BUILD_NUMBER_OFFSET] = int(new_version_list[2])
        mock_read_config_block.return_value = test_data

        (updated, current_version) = self.backend.update_board_config_version()

        mock_hid_transport.connect.assert_called_with(serial_number=self.USB_SERIAL_SUBSTRING, product='nedbg')
        mock_hid_transport.disconnect.assert_called()
        mock_write_config_block.assert_not_called()
        mock_read_config_block.assert_called_with(False)

        self.assertFalse(updated,
                         msg="Version update did happen even though now new versions should exist (returned True)")
        self.assertEqual(current_version, new_version, msg="Unexpected version reported after update")

    def test_generate_hex_when_both_board_and_device_xml_is_none_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.backend.generate_hex(None, None)

    def test_generate_hex_device_config_and_board_config(self):
        devicename = "ATmega4809"
        progbase = 0x4000
        flashsize = 0xC000

        hexfile_name = self.backend.generate_hex(self.BOARD_CONFIG_FILE_PATH, self.DEVICE_CONFIG_FILE_PATH)

        self.assertTrue(os.path.exists(hexfile_name))

        ihex = IntelHex(hexfile_name)

        self._check_devicename_hexfile(devicename, ihex)
        self._check_flashsize_hexfile(flashsize, ihex)
        self._check_progbase_hexfile(progbase, ihex)

        # Clean up by removing the generated file
        os.remove(hexfile_name)

    def test_generate_hex_device_config_only(self):
        progbase = 0x4000
        flashsize = 0xC000

        hexfile_name = self.backend.generate_hex(None, self.DEVICE_CONFIG_FILE_PATH)

        self.assertTrue(os.path.exists(hexfile_name))

        ihex = IntelHex(hexfile_name)

        self._check_flashsize_hexfile(flashsize, ihex)
        self._check_progbase_hexfile(progbase, ihex)
        self._check_empty_config(self.USER_CONFIG_START_ADDRESS, self.CONFIG_END_ADDRESS, ihex)

        # Clean up by removing the generated file
        os.remove(hexfile_name)

    def test_generate_hex_board_config_only(self):
        devicename = "ATmega4809"

        hexfile_name = self.backend.generate_hex(self.BOARD_CONFIG_FILE_PATH)

        self.assertTrue(os.path.exists(hexfile_name))

        ihex = IntelHex(hexfile_name)

        self._check_devicename_hexfile(devicename, ihex)
        self._check_empty_config(self.DEVICE_CONFIG_ADDRESS, self.USER_CONFIG_START_ADDRESS, ihex)

        # Clean up by removing the generated file
        os.remove(hexfile_name)
