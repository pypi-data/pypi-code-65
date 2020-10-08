"""
Backend interface for the pydebuggerconfig utility.

This module is the boundary between the Command Line Interface (CLI) part and
the backend part that does the actual job.  Any external utility or script that
needs access to the functionality provided by pydebuggerconfig should connect to the
interface provided by this backend module
"""
import os.path
from logging import getLogger
from contextlib import contextmanager
from intelhex import IntelHex

from pyedbglib.hidtransport.hidtransportfactory import hid_transport

from .boardconfig import BoardConfig
from .deviceconfig import DeviceConfig
from .pydebuggerconfig_errors import PydebuggerconfigToolConnectionError

# Currently only PKOB nano (nEDBG) is supported
TOOLNAME = 'nedbg'

@contextmanager
def board_config_manager(serialnumber_substring=''):
    """Context manager handling BoardConfig instantiation and teardown

    This makes it possible to instantiate a BoardConfig object and automatically handle the setup and teardown of the
    debugger connection.
    Example:
        ``with board_config_manager(serialnumber_substring=serialnumber_substring) as board_cfg:
            # Use the BoardConfig instance for something
            board_cfg.config_read_from_board()

        # When the code execution reaches the end of the with block the finally block is run which will disconnect
        # from the debugger``

    :param serialnumber_substring: Serial number of debugger to connect to.  Can be an empty string or a subset of
            a serial number.  Not case sensitive.  This function will do matching of the last part of the devices serial
            numbers to the serialnumber_substring
            Examples:
                * '123' will match "MCHP3252000000043123" but not "MCP32520001230000000"
                * '' will match any serial number
    :type serialnumber_substring: str
    :yield: BoardConfig instance
    :rtype: class:pydebuggerconfig.boardconfig.BoardConfig
    :raises:
        PydebuggerconfigToolConnectionError if connecting to tool/debugger failed
    """
    board_config = BoardConfig()
    transport = hid_transport()
    try:
        if not transport.connect(serial_number=serialnumber_substring, product=TOOLNAME):
            raise PydebuggerconfigToolConnectionError(
                "Could not find exactly one tool with a USB serial ending in '{}'".format(serialnumber_substring))
    except IOError as e_message:
        raise PydebuggerconfigToolConnectionError("Error connecting to tool: {}".format(e_message))
    board_config.transport_set(transport)
    try:
        yield board_config
    finally:
        transport.disconnect()

@contextmanager
def device_config_manager(serialnumber_substring=''):
    """Context manager handling DeviceConfig instantiation and teardown

    This makes it possible to instantiate a DeviceConfig object and automatically handle the setup and teardown of the
    debugger connection.
    Example:
        ``with device_config_manager(serialnumber_substring=serialnumber_substring) as device_cfg:
            # Use the DeviceConfig instance for something
            device_cfg.config_read_from_board()

        # When the code execution reaches the end of the with block the finally block is run which will disconnect
        # from the debugger``

    :param serialnumber_substring: Serial number of debugger to connect to.  Can be an empty string or a subset of
            a serial number.  Not case sensitive.  This function will do matching of the last part of the devices serial
            numbers to the serialnumber_substring
            Examples:
                * '123' will match "MCHP3252000000043123" but not "MCP32520001230000000"
                * '' will match any serial number
    :type serialnumber_substring: str
    :yield: DeviceConfig instance
    :rtype: class:pydebuggerconfig.deviceconfig.DeviceConfig
    :raises:
        PydebuggerconfigToolConnectionError if connecting to tool/debugger failed
    """
    device_config = DeviceConfig()
    transport = hid_transport()
    try:
        if not transport.connect(serial_number=serialnumber_substring, product=TOOLNAME):
            raise PydebuggerconfigToolConnectionError(
                "Could not find exactly one tool with a USB serial ending in '{}'".format(serialnumber_substring))
    except IOError as e_message:
        raise PydebuggerconfigToolConnectionError("Error connecting to tool: {}".format(e_message))
    device_config.transport_set(transport)
    try:
        yield device_config
    finally:
        transport.disconnect()

class Backend(object):
    """
    Backend interface of the pydebuggerconfig utility.

    This class provides access to all the functionality provided by pydebuggerconfig.
    """
    API_VERSION = '1.0'

    def __init__(self, serialnumber_substring=''):
        """
        :param serialnumber_substring: USB Serial number of debugger to connect to. It can be a full serial number, an
            empty string or a subset of a serial number.  It is not case sensitive.  The serial number matching is done
            by comparing the ``serialnumber_substring`` to the last part of the USB serial numbers of the connected
            debuggers.
            Examples:
                * '123' will match "MCHP3252000000043123" but not "MCP32520001230000000"
                * '' will match any serial number
        :type serialnumber_substring: str
        """
        # Hook onto logger
        self.logger = getLogger(__name__)
        self.serialnumber_substring = serialnumber_substring

    def get_api_version(self):
        """
        Returns the current pydebuggerconfig API version

        :return: pydebuggerconfig backend API version
        :rtype: str
        """
        return self.API_VERSION

    @staticmethod
    def get_board_config_as_string(board_xml_file):
        """Get a string representation of the board config xml file content

        The returned string is typically useful for printing the config data to console
        :param board_xml_file: File path to xml file containing board/kit specific configuration data.  The file path
            can be absolute or relative to pydebuggerconfig folder, e.g. "board-configs/ATmega4809-CNANO.xml"
        :type board_xml_file: str
        :return: String representation of the board config xml file content
        :rtype: str
        """
        board_cfg = BoardConfig()
        board_cfg.config_open_xml(board_xml_file)
        return board_cfg.config_array_print('xml')

    @staticmethod
    def get_device_config_as_string(device_xml_file):
        """Get a string representation of the device config xml file content

        The returned string is typically useful for printing the config data to console
        :param device_xml_file: File path to xml file containing device specific configuration data.  The file path can
            be absolute or relative to pydebuggerconfig folder, e.g. "device-configs/ATmega4809-device-blob.xml"
        :type device_xml_file: str
        :return: String representation of the device config xml file content
        :rtype: str
        """
        device_cfg = DeviceConfig()
        device_cfg.config_open_xml(device_xml_file)
        return device_cfg.config_array_print('xml')

    def read_board_config_as_string(self, factory_config=False):
        """Read out board config from the debugger and return string representation of content

        :param factory_config: If True the factory board config will be read out, defaults to False
        :type factory_config: bool, optional
        :return:  String representation of the board config read from debugger
        :rtype: str
        :raises:
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with board_config_manager(serialnumber_substring=self.serialnumber_substring) as board_cfg:
            board_cfg.config_read_from_board(factory=factory_config)

            return board_cfg.config_array_print('board')

    def read_device_config_as_string(self):
        """Read out device config from the debugger and return string representation of content

        :return:  String representation of the device config read from debugger
        :rtype: str
        :raises:
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with device_config_manager(serialnumber_substring=self.serialnumber_substring) as device_cfg:
            device_cfg.config_read_from_board()

            return device_cfg.config_array_print('board')

    def write_board_config(self,
                           board_xml_file,
                           factory_config=False,
                           serialnumber=None,
                           preserve=None):
        """Write board config data to debugger

        :param board_xml_file: File path to xml file containing board/kit specific configuration data.  The file path
            can be absolute or relative to pydebuggerconfig folder, e.g. "board-configs/ATmega4809-CNANO.xml".
        :type board_xml_file: str
        :param factory_config: If True the factory board config will be written in addition to the user config,
            defaults to False.  Also if True the preserved values will come from the factory config.
        :type factory_config: bool, optional
        :param serialnumber: Board serial number to program (20 ASCII characters), defaults to None.  Overrides the
            serial number from the board config xml file if it is not None
        :type serialnumber: str, optional
        :param preserve: List of registers to preserve, defaults to None.  Registers in the list will keep their values
            and any values in the board xml file will be ignored.
        :type preserve: list[str], optional
        :return: Human readable string representation of the board config written to the debugger
        :rtype: str
        :raises:
            PydebuggerconfigError: if any of the registers given in the preserve parameter are invalid
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with board_config_manager(serialnumber_substring=self.serialnumber_substring) as board_cfg:
            # Open the product xml file
            board_cfg.config_open_xml(board_xml_file)

            if serialnumber is not None:
                # Overwriting the serial number
                board_cfg.serial_set(serialnumber)

            if preserve is not None:
                # Read the config for the case of preserving registers
                board_cfg.config_read_from_board(factory=factory_config)
                for register in preserve:
                    value = board_cfg.register_get(register, 'board').strip('\0')
                    msg = "Preserving register {}: '{}'".format(register, value)
                    self.logger.info(msg)
                    board_cfg.register_set(register, value, 'xml')

            self.logger.info("Writing user configuration.")
            board_cfg.config_program(factory=False)
            if factory_config:
                self.logger.info("Writing factory configuration.")
                board_cfg.config_program(factory=True)

            return board_cfg.config_array_print('xml')

    def write_device_config(self, device_xml_file):
        """Write device config data to debugger

        :param device_xml_file: File path to xml file containing device specific configuration data.  The file path can
            be absolute or relative to pydebuggerconfig folder, e.g. "device-configs/ATmega4809-device-blob.xml"
        :type device_xml_file: str
        :return: Human readable string representation of the device config written to the debugger
        :rtype: str
        :raises:
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with device_config_manager(serialnumber_substring=self.serialnumber_substring) as device_cfg:
            # Open the device blob xml file
            device_cfg.config_open_xml(device_xml_file)
            self.logger.info("Writing device specific configuration.")
            device_cfg.config_program()

            return device_cfg.config_array_print('xml')

    def replace(self, registers_dict, factory_config=False):
        """Replace one or more registers in the debugger board config section

        Provided register values will replace the ones in the debugger board config section while the rest of the
        registers will be left unchanged
        :param registers_dict: Dictionary with register names as keys and register values as values
            Example:
                registers_dict={'KITNAME': 'My kitname', 'SERNUM': 01234567890123456789}
        :type registers_dict: dict(str, str/int/list[int]/list[str])
        :param factory_config:  If True the factory board config section will be written instead of the
            user config section, defaults to False
        :type factory_config: bool, optional
        :raises:
            PydebuggerconfigError: if any of the given register names or values are invalid
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with board_config_manager(serialnumber_substring=self.serialnumber_substring) as board_cfg:
            board_cfg.config_read_from_board(factory=factory_config)
            for register in registers_dict:
                value = registers_dict[register]
                message = "Writing {} into register {}...".format(value, register)
                self.logger.info(message)
                # Replace the value
                board_cfg.register_set(register, value, 'board')

            # Write back to the board
            board_cfg.config_program(source='board', factory=factory_config)

    def restore_board_config(self):
        """Restore factory board configuration

        Reads out the factory board configuration from the debugger and writes it back to the user board configuration
        section
        :raises:
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with board_config_manager(serialnumber_substring=self.serialnumber_substring) as board_cfg:
            self.logger.info("Reading factory configuration")
            board_cfg.config_read_from_board(factory=True)
            self.logger.info("Writing user configuration")
            board_cfg.config_program(source='board', factory=False)

    def update_board_config_version(self):
        """Update board config to latest specification version

        Only updates specification to latest minor version, keeping the major version the same
        :return: (updated, config_version) where updated is True if a newer version was found and the board config
            version was updated, if False no update was done.  config_version is the current version of the config
            after the update.
        :rtype: tuple(bool, str)
        :raises:
            PydebuggerconfigToolConnectionError: if connecting to tool/debugger failed
        """
        with board_config_manager(serialnumber_substring=self.serialnumber_substring) as board_cfg:
            board_cfg.config_read_from_board(factory=False)
            (update_found, current_version) = board_cfg.specification_update()
            if update_found:
                self.logger.info("Updating board config (user) version to %s", current_version)
                board_cfg.config_program(source='board', factory=False)
            else:
                self.logger.info("Board config specification is up to date, %s", current_version)

        return (update_found, current_version)

    def generate_hex(self, board_xml_file=None, device_xml_file=None):
        """Generate hex file from board config xml file and/or device config xml file

        The generated hex file can be programmed directly into the debugger flash, typically during production
        At least one of the board_xml_file and device_xml_file parameters must be defined (not None)
        :param board_xml_file: File path to xml file containing board/kit specific configuration data, defaults to None.
            The file can be absolute or relative to pydebuggerconfig folder, e.g. "board-configs/ATmega4809-CNANO.xml"
        :type board_xml_file: str
        :param device_xml_file: File path to xml file containing device specific configuration data, defaults to None
            The file can be absolute or relative to pydebuggerconfig folder,
            e.g. "device-configs/ATmega4809-device-blob.xml"
        :type device_xml_file: str
        :return: Path to file generated
        :rtype: str
        :raises:
            ValueError: If both board_xml_file and device_xml_file are None
        """
        if board_xml_file is None and device_xml_file is None:
            raise ValueError("At least one of board_xml_file and device_xml_file must be given")

        # Only nEDBG for now
        nedbg_device_config_offset = 0x3F100
        nedbg_user_config_offset = 0x3FC00
        nedbg_factory_config_offset = 0x3FE00

        # Root filename
        filename = "generated_config"

        # Create a new hexfile
        ihex_obj = IntelHex()

        # Board
        if board_xml_file is not None:
            board_cfg = BoardConfig()
            # Open the board xml file and extract the data
            board_cfg.config_open_xml(board_xml_file)
            data = board_cfg.data_array['xml']

            # Copy config data to both user and factory config in the hexfile
            for index, value in enumerate(data):
                ihex_obj[nedbg_user_config_offset + index] = value
                ihex_obj[nedbg_factory_config_offset + index] = value

            # Name the file according to incoming board config name
            filename += "_{0:s}".format(os.path.basename(os.path.splitext(board_xml_file)[0]))

        # Device
        if device_xml_file is not None:
            device_cfg = DeviceConfig()
            # Open the device xml file and extract the data
            device_cfg.config_open_xml(device_xml_file)
            data = device_cfg.data_array['xml']

            # Copy config data to device config area
            for index, value in enumerate(data):
                ihex_obj[nedbg_device_config_offset + index] = value

            # Name the file according to incoming device config name
            filename += "_{0:s}".format(os.path.basename(os.path.splitext(device_xml_file)[0]))

        # Generate output
        filename += ".hex"
        filename = os.path.normpath(filename)
        ihex_obj.write_hex_file(filename)
        self.logger.info("Written data to '{0:s}'".format(filename))

        return filename
