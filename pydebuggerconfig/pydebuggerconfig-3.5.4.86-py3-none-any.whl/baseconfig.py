"""
Base configuration class
"""
from __future__ import print_function
import glob
import os
import xml.etree.ElementTree as ETree
from logging import getLogger
import xmlschema

# pyedbglib dependencies
import pyedbglib.protocols.configprotocol as configprotocol

from .pydebuggerconfig_errors import PydebuggerconfigError, PydebuggerconfigToolConnectionError


class BaseConfig(object):
    """
    Base class to work with configuration data for the PKOB nano (nEDBG) debugger from Microchip

    This class is not useful on its own, it should be extended by using it as parent for classes handling specific
    config sections like board config and device config.
    """
    # Register names for the major, minor and build version in the specification
    MAJOR_REGISTER = "CONFIG_FORMAT_MAJOR"
    MINOR_REGISTER = "CONFIG_FORMAT_MINOR"
    BUILD_REGISTER = "CONFIG_FORMAT_BUILD"

    PRETTY_NAME = "Base Configuration"

    XML_ROOT_NAME = "configuration"

    # Used to find specification xml files on disk
    PATH = os.path.abspath(os.path.dirname(__file__))
    SPECIFICATION_FOLDER = os.path.join(PATH, "config-specification")
    SPECIFICATION_NAME = None

    def __init__(self):
        # Logger object
        self.logger = getLogger(__name__)

        # Storage for configuration xml
        self.config_xml = None

        # Storage for configuration specification xml
        self.specification_xml = {'board': None, 'xml': None}

        # XML instance schema
        self.schema = None

        # Placeholders for configuration data arrays
        self.data_array = {'board': [], 'xml': []}

        # Storage for version numbers
        self.major = {'board': 0, 'xml': 0}
        self.minor = {'board': 0, 'xml': 0}
        self.build = {'board': 0, 'xml': 0}

        # Transport placeholders
        self.transport_connected = False
        self.transport = None

        # Protocol to read/write data
        self.protocol = configprotocol.ConfigProtocol(None)

    def transport_set(self, transport):
        """
        Sets up a transport to transfer configuration data

        :param transport: handle to transport object
        :type transport: class:cyhidapi:CyHidApiTransport or equivalent
        """
        self.logger.debug("Setting tool transport")
        self.transport = transport
        self.protocol.set_transport(self.transport)
        self.transport_connected = True

    def transport_check(self):
        """
        Is a transport set up ?

        raises:
            PydebuggerconfigToolConnectionError: if no transport has been set
        """
        if not self.transport_connected:
            raise PydebuggerconfigToolConnectionError("No tool is connected, add a tool with toolSet()")

    def specification_open(self, source, filepath=None):
        """
        Open a specification file from disk

        :param source: either 'board' or 'xml'
        :type source: str
        :param filepath: The full path to a specific specification file or None
                  If 'None', a file will automatically be found
        :type filepath: str
        """
        self.logger.debug("Open specification file to parse %s data", source)
        if filepath is None:
            filepath = self.specification_find_on_disk(source)

        filepath = os.path.normpath(filepath)

        self.logger.info("Opening specification file: %s", filepath)
        # Open the specification file
        self.specification_xml[source] = ETree.parse(filepath)
        # Open the xsd validation file
        self.schema = xmlschema.XMLSchema(filepath.replace('.xml', '.xsd'))

    def specification_find_on_disk(self, source):
        """
        Finds a specification on disk for configuration data read from a board or an xml file

        :param source: Either 'board' or 'xml'
        :type source: str
        """
        # General file version pattern:
        pattern = "*[0-9].*[0-9].*[0-9]"
        ext = 'xml'

        # Try to find a file that matches the version
        version = "{}.{}.{}".format(self.major[source], self.minor[source], self.build[source])

        path = os.path.join(self.SPECIFICATION_FOLDER, self.SPECIFICATION_NAME)

        self.logger.debug("Looking for file with version: %s", version)
        files = glob.glob('{}-{}.{}'.format(path, version, ext))

        if len(files) != 1:
            # Did not find an exact match for this version, try to find one that is close
            self.logger.warning("Did not find specification xml with exact match for version %s", version)
            # https://jira.microchip.com/browse/DSG-2200: How do we handle version mismatch?
            files = glob.glob('{}-{}.{}'.format(path, pattern, ext))

        self.logger.debug(files)

        if not files:
            raise PydebuggerconfigError("Could not find any configuration specification file with the pattern {}-{}.{}"
                                        .format(path, pattern, ext))

        return files[0]

    def config_open_xml(self, filepath):
        """
        Open a configuration xml file and prepare it for programming

            1. Open the configuration xml file
            2. Find the version numbers
            3. Open specification + xml schema
            4. Validate the configuration xml file with schema
            5. Check that the input is a valid configuration
            6. Convert to array ready for programming
        :param filepath:  Path to a specific specification file, either absolute or relative to pydebuggerconfig
            folder, e.g. board-configs/ATmega4809-CNANO.xml
        :param filepath: str
        """
        filepath = os.path.normpath(filepath)
        filepath_internal = filepath.replace("-configs", "-configs-internal")
        # Possible paths to XML file
        filepaths = [filepath, # Absolute path
                     filepath_internal, # Absolute path to interna folder
                     os.path.join(self.PATH, filepath), # Relative path
                     os.path.join(self.PATH, filepath_internal)] # Relative path to internal folder
        index = 0
        filepath_final = filepaths[index]
        while not os.path.exists(filepath_final):
            self.logger.debug("Could not find %s", filepath_final)
            index += 1
            if index >= len(filepaths):
                raise IOError("Could not open file: {}".format(filepath))
            filepath_final = filepaths[index]

        self.logger.info("Opening board file \'%s\'", filepath_final)
        self.config_xml = ETree.parse(filepath_final)

        # Check that the root node name is correct
        root = self.config_xml.getroot()
        if root.tag != self.XML_ROOT_NAME:
            msg = "{} is not a valid {}".format(filepath_final, self.PRETTY_NAME)
            self.logger.error(msg)
            raise PydebuggerconfigError(msg)

        # Find major, minor and build number from the .xml file
        major = self.config_xml.findall("./register[@name='{}']".format(self.MAJOR_REGISTER))[0].attrib['value']
        minor = self.config_xml.findall("./register[@name='{}']".format(self.MINOR_REGISTER))[0].attrib['value']
        build = self.config_xml.findall("./register[@name='{}']".format(self.BUILD_REGISTER))[0].attrib['value']

        self.logger.debug("Found version from product XML: %s.%s.%s", major, minor, build)

        self.major['xml'] = self.string_value_to_int(major)
        self.minor['xml'] = self.string_value_to_int(minor)
        self.build['xml'] = self.string_value_to_int(build)

        # Automatically open a specification xml based on the version
        self.specification_open('xml')

        # XSD validation of the xml file
        self.schema.validate(filepath_final)

        # Check that we know where to put the data in the XML
        self.config_check_xml()

        # Initialize an empty config array
        self.config_array_create_empty('xml')

        # Put registers in the array
        self.config_xml_to_array()

    def config_check_xml(self):
        """
        Compares the registers in self.config_xml with the specification in self.specification_xml['xml']

        Checks that we know where to put all the defined registers in the product XML
        :raises:
            PydebuggerconfigError: when configuration does not match the specification
        """
        valid = True
        for register in self.config_xml.findall('register'):
            name = register.attrib['name']
            match = self.specification_xml['xml'].findall("./registers/register[@name='{}']".format(name))
            if not match:
                self.logger.error("No match for register: %s", name)
                valid = False

        if not valid:
            msg = "Configuration does not match the specification"
            self.logger.error(msg)
            raise PydebuggerconfigError(msg)

    def config_xml_to_array(self):
        """
        Convert opened configuration xml to a byte list ready for programming

        :raises:
            PydebuggerconfigError: when a configuration register is missing a value
        """
        # Loop through the config specification and find values from the product XML
        for register in self.specification_xml['xml'].findall("./registers/register"):
            # Get register parameters from the specification
            name = register.attrib['name']
            offset = self.string_value_to_int(register.attrib['offset'])

            # Get the value from the product XML
            product_config = self.config_xml.find("./register[@name='{}']".format(name))
            value = None
            if product_config is not None:
                if 'value' in product_config.attrib:
                    value = product_config.attrib['value']
            else:
                msg = "No value defined for register {} in the config xml file".format(name)
                self.logger.error(msg)
                raise PydebuggerconfigError(msg)

            self.logger.debug("Validating %s as value in the %s register", value, name)
            self._check_register_value(register, value)

            data = self._get_data_as_list(register, value)

            # Put data in the config array
            for i, byte in enumerate(data, 0):
                address = offset + i
                if self.data_array['xml'][address] != 0:
                    self.logger.error("Overwrite detected at address 0x%X", address)
                self.data_array['xml'][address] = byte

    def _get_data_as_list(self, register, value):
        """Return list representation of register data"""
        # Get register parameters from the specification
        size = self.string_value_to_int(register.attrib['size'])
        register_type = register.attrib['type']

        # Convert data based on register type
        if register_type == "STRING":
            # USB friendly data conversion
            data = self.protocol.fix(value)
        elif register_type in ("ENUM", "BYTE", "BITS"):
            # USB friendly data conversion
            data = self.protocol.fix(self.value_to_array_8bit(value, size))
        elif register_type == "ARRAY":
            data = self.protocol.fix(self.string_to_array(value))
        elif register_type == "BLOB":
            data = []  # This is a device config type
        else:
            self.logger.error("Unknown data type %s", register_type)
            data = []

        return data

    def _check_register_value(self, register, value):
        """Check that the value of the register is valid based on register type"""
        # Get register parameters from the specification
        name = register.attrib['name']
        size = self.string_value_to_int(register.attrib['size'])
        register_type = register.attrib['type']

        # Check the register value based on register type
        if register_type == "ENUM":
            self._check_enum_register(register, value, name)

        elif register_type == "BYTE":
            self._check_byte_register(size, value, name)

        elif register_type == "ARRAY":
            if value == 0:
                value = "00"
            self._check_array_register(size, value, name)

        elif register_type == "BITS":
            self._check_bits_register(register, size, value, name)

    def _check_enum_register(self, register, value, name):
        """Check that the value is a valid setting"""
        valid = register.find("./value[@value='{}']".format(value))
        if valid is None:
            valid = register.find("./value[@value='0x{:02X}']".format(int(value, 0)))
        if valid is None:
            self.logger.error("Value %d is an unknown ENUM in the register %s", value, name)

    def _check_byte_register(self, size, value, name):
        """
        Check that the number fits in the register

        :raises:
            PydebuggerconfigError: when value is too big to fit the register
        """
        max_value = 2 ** (size * 8) - 1
        if self.string_value_to_int(value) > max_value:
            msg = "Value {} in register {} is larger than the maximum value of {}"\
                .format(value, name, max_value)
            self.logger.error(msg)
            raise PydebuggerconfigError(msg)

    def _check_array_register(self, size, value, name):
        """
        Check that the value can fit in the register

        :raises:
            PydebuggerconfigError: when value does not fit the register
        """
        if len(value)/2 > size:
            msg = "Value {} in register {} has a length longer than the maximum of {}".format(value, name, size)
            self.logger.error(msg)
            raise PydebuggerconfigError(msg)

    def _check_bits_register(self, register, size, value, name):
        """Check if unknown bits are set"""
        bits = []
        for bit in register.findall("./bits"):
            pos = self.string_value_to_int(bit.attrib['pos'])
            bits.append(pos)

        for i in range(0, size * 8):
            if i not in bits:
                if self.string_value_to_int(value) & (1 << i):
                    self.logger.warning("Value %s sets unknown bit %d in register %s", value, i, name)


    def config_array_to_xml(self, filepath):
        """
        Generate a configuration XML

        Generate a configuration file based on:
        self.data_array['board']
        self.specification_xml['board']

        save the file to "filepath"

        :param filepath: Path to XML file to write to
        :type filepath: str
        :raises:
            NotImplementedError: as this method needs to be overridden.
        """
        # https://jira.microchip.com/browse/DSG-2197
        raise NotImplementedError("config_array_to_xml is not implemented.")

    def config_program(self, source='xml', factory=False):
        """
        Programs the board configuration with the chosen transport

        :param source: either 'board' or 'xml'
        :type source: str
        :param factory: if True the factory section will be written, if False the user section will be written
        :type factory: bool
        :raises:
            NotImplementedError: as this method needs to be overridden.
        """
        raise NotImplementedError("method needs to be defined by sub-class")

    def config_read_from_board(self, source='board', factory=False):
        """
        Read board configuration from the connected board

        :param source: either 'board' or 'xml'
        :type source: str
        :param factory: if True the factory section will be read, if False the user section will be read
        :type factory: bool
        :raises:
            NotImplementedError: as this method needs to be overridden.
        """
        raise NotImplementedError("method needs to be defined by sub-class")

    def register_get(self, register, source='board'):
        """
        Get the data in the register

        :param register: Name of the register
        :type register: str
        :param source: 'xml' or 'board'
        :type source: str
        :return: register value
        :rtype: str/int/list[int]/list[str]
        :raises:
            PydebuggerconfigError: if register does not exist
        """

        # Find information about the register to replace
        reg = self.specification_xml[source].find("./registers/register[@name='{}']".format(register))
        if reg is None:
            raise PydebuggerconfigError("Register {} does not exist.".format(register))
        size = self.string_value_to_int(reg.attrib['size'])
        offset = self.string_value_to_int(reg.attrib['offset'])
        regtype = reg.attrib['type']

        # Convert the data based on the register type
        data = self.data_array[source][offset:offset+size]
        if regtype == 'STRING':
            return ''.join(chr(item) for item in data)
        if regtype == "ARRAY":
            return data

        value = 0
        for i, byte in enumerate(data):
            value += (byte & 0xFF) << (i * 8)
        return "0x{:0{}x}".format(value, size*2)

    def register_set(self, register, data, source='xml'):
        """
        Replace the data in the register

        :param register: Name of the register
        :type register: str
        :param data: data to put into the register
        :type data: str/int/list[int]/list[str]
        :param source: 'xml' or 'board'
        :type source: str
        :raises:
            PydebuggerconfigError: if data does not fit in the register
        """

        # Find information about the register to replace
        reg = self.specification_xml[source].find("./registers/register[@name='{}']".format(register))
        if reg is None:
            raise PydebuggerconfigError("Register {} does not exist.".format(register))
        name = reg.attrib['name']
        size = self.string_value_to_int(reg.attrib['size'])
        offset = self.string_value_to_int(reg.attrib['offset'])
        regtype = reg.attrib['type']

        # Convert the data based on the register type
        if regtype  in ('STRING', 'ARRAY'):
            if len(data) > size:
                msg = "{} can fit {} characters, '{}' is {} characters long".format(name, size, data, len(data))
                raise PydebuggerconfigError(msg)
            data = self.protocol.fix(data)
        else:
            data = self.value_to_array_8bit(data, size)

        self.logger.info("Replacing the value of the %s register with %s", name, data)

        # Zero out register
        for i in range(size):
            self.data_array[source][offset+i] = 0x00

        # Replace the data
        for i, byte in enumerate(data, 0):
            self.data_array[source][offset+i] = byte

    def config_array_create_empty(self, source):
        """
        Creates and empty config array in self.config_data[source]

        :param source: 'xml' or 'board'
        :type source: str
        :raises:
            NotImplementedError: as this method needs to be overridden.
        """
        raise NotImplementedError("method needs to be defined by sub-class")

    def config_array_print(self, source):
        # This function should be refactored to be part of config_array_to_xml,
        # see https://jira.microchip.com/browse/DSG-2198
        """
        Decode a board configuration array with self.specification_xml[source]

        :param source: 'xml' or 'board'
        :type source: str
        :returns: Human-readable string representation of the config
        :rtype: str
        """

        string = "\n"

        # In case we have unknown bits set, we need to report it:
        filled = []

        for register in self.specification_xml[source].findall("./registers/register"):
            # Get register parameters from the specification
            name = register.attrib['name']
            offset = self.string_value_to_int(register.attrib['offset'])
            size = self.string_value_to_int(register.attrib['size'])
            regtype = register.attrib['type']
            caption = register.attrib['caption']

            # Keep track of bytes we decoded:
            for i in range(0, size):
                filled.append(offset + i)

            data = self.data_array[source][offset:offset + size]
            value = None
            padding = ' ' * (24 - len(name))
            string += ("Register {}:{}".format(name, padding))

            # Decode content
            if regtype == "BITS":
                string += self._get_bits_register_as_string(register, data)
            elif regtype == "ENUM":
                string += self._get_enum_register_as_string(register, data)
            elif regtype == "BYTE":
                value = self.array_8bit_to_value(data)
                string += "0x{0:0{1}X} ({0})  # {2}".format(value, size * 2, caption)
            elif regtype == "STRING":
                string += self._get_string_register_as_string(register, data)
            elif regtype == "ARRAY":
                value = ""
                for i, byte in enumerate(data, 0):
                    value += "0x{:02X}, ".format(byte)
                value = value.strip(', ')
                string += '[' + value + ']'

            string += "\n"

        self.logger.debug(string)

        for i in range(0, len(self.data_array[source])):
            if i not in filled:
                if self.data_array[source][i]:
                    self.logger.warning("Found data at address %04X that is unknown to this config", i)

        return string

    def _get_bits_register_as_string(self, register, data):
        padding = ' ' * 38
        name = register.attrib['name']
        size = self.string_value_to_int(register.attrib['size'])
        caption = register.attrib['caption']
        value = self.array_8bit_to_value(data)
        string = ''

        # Add raw value
        string += "0x{0:0{1}X} ({0})  # {2}".format(value, size * 2, caption)

        # Add bit descriptions
        bits = []
        next_bit = 0
        for bit in register.findall("./bits"):
            string += "\n"
            pos = self.string_value_to_int(bit.attrib['pos'])
            bitname = bit.attrib['name']
            if (1 << pos) & value:
                bit_value = 1
            else:
                bit_value = 0

            # Fill in "Reserved" for all empty bit positions up to the next non-empty bit
            for bitindex in range(next_bit, pos):
                string += "{}bit {}, Reserved\n".format(padding, bitindex)

            string += "{}bit {}, {}: {} ".format(padding, pos, bitname, bit_value)
            string += "# {}".format(bit.attrib['caption'])
            bits.append(pos)
            next_bit = pos+1

        self.logger.debug("%s: %d", name, value)
        self.logger.debug(bits)

        # Find all bits that are set in the value, but are not known to the specification
        for i in range(0, size * 8):
            # Is the bit 1?
            if (1 << i) & value:
                # Is the bit unknown?
                if i not in bits:
                    self.logger.warning("Unknown bit %d is set in the %s register", i, name)

        return string

    def _get_enum_register_as_string(self, register, data):
        padding = ' ' * 38
        string = ''
        name = register.attrib['name']
        size = self.string_value_to_int(register.attrib['size'])
        caption = register.attrib['caption']

        value = self.array_8bit_to_value(data)
        string += "0x{0:0{1}X} ({0})  # {2}".format(value, size * 2, caption)

        string += "\n"
        res = register.findall("./value[@value='0x{:0{}X}']".format(value, size * 2))
        if res:
            attrib = res[0].attrib
            string += "{}ENUM {}, {}: {}".format(padding, attrib['value'], attrib['name'], attrib['caption'])
        else:
            self.logger.warning("Unknown ENUM value %d found in register %s", value, name)
            string += "{}ENUM: UNKNOWN ENUM".format(padding)

        return string

    @staticmethod
    def _get_string_register_as_string(register, data):
        caption = register.attrib['caption']
        value = ""
        string = ''

        for byte in data:
            character = chr(byte)
            if character == '\0':
                break
            value += character

        string += '\"' + value + '\"'
        string += " # {}".format(caption)

        return string


    @staticmethod
    def string_value_to_int(string):
        """
        Takes a string that represents a number and convert it to int.

        Works with ASCII digits "255" and hex notation "0xFF".
        :param string: string representation of a number
        :param string: str
        :return: int value
        :rtype: int
        """
        if isinstance(string, str) is False:
            return string

        # Hex notation "0xFF"
        if string.startswith("0x"):
            value = int(string, 16)
        # ASCII Digits "255"
        else:
            value = int(string)

        return value

    def value_to_array_8bit(self, value, size):
        """
        Converts an int to a multi-byte array

        :param value: int value to convert
        :type value: int
        :param size: number of bytes in the array to be generated
        :type size: int
        :return: list of bytes representing the value
        :rtype: list[byte]
        """
        tmp = []
        for i in range(0, size):
            tmp.append(int((self.string_value_to_int(value) & (0xFF << i * 8)) >> i * 8))
        tmp = list(tmp)
        return tmp

    def array_8bit_to_value(self, array):
        """
        Converts a multi-byte array to an int

        :param array: list of bytes
        :type array: list[byte]
        :return: int value representing the array
        :rtype: int
        """
        value = 0
        tmp = list(array)
        for i, byte in enumerate(tmp, 0):
            value += (byte & 0xFF) << (i * 8)
        self.logger.debug("array_8bit_to_value converted %s to %d", array, value)
        return value

    def string_to_array(self, string):
        """
        Converts a string to a list of byte values

        :param string: string representing a list of bytes in hex format, e.g. '0x01, 0x02, 0x03'
        :type string: str
        :return: list of byte values
        :rtype: list[byte]
        """
        value = list(bytearray.fromhex(string))
        self.logger.debug("string_to_array converted %s to %s", string, ' '.join(map(str, value)))
        return value
