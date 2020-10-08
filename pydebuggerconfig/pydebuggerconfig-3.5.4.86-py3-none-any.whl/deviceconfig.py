"""
device configuration class
"""
from logging import getLogger
import crcmod

# pyedbglib dependencies
import pyedbglib.protocols.configprotocol as configprotocol

from .baseconfig import BaseConfig
from .pydebuggerconfig_errors import PydebuggerconfigError

class DeviceConfig(BaseConfig):
    """
    Helper class to work with device configuration data for the PKOB nano (nEDBG) debugger from Microchip
    """
    # Register names for the major, minor and build data
    MAJOR_REGISTER = "DEVICE_CONFIG_MAJOR"
    MINOR_REGISTER = "DEVICE_CONFIG_MINOR"
    BUILD_REGISTER = "DEVICE_CONFIG_BUILD"

    PRETTY_NAME = "Device Configuration"

    XML_ROOT_NAME = "deviceconf"

    SPECIFICATION_NAME = "device_config_defines"

    def __init__(self):
        BaseConfig.__init__(self)

        # Logger object
        self.logger = getLogger(__name__)

        self.data_end = {'board': 0, 'xml': 0}

        # CRC-16 calculation
        # CRC16-CCIT, poly = 0x1021, init-value = 0xFFFF, reversed = False, XOR-out = 0x0000
        self.crc = crcmod.predefined.mkCrcFun('crc-ccitt-false')

    def config_xml_to_array(self):
        """
        Converts the register values in the product xml to an array using the config specification

        product: self.board_xml
        specification: self.specification_xml['xml']
        """
        # Put regular registers in the array
        BaseConfig.config_xml_to_array(self)

        # Put the blob in the array
        self.blob_xml_to_array()

        # Calculate the content length and the checksum
        self.calculate_checksum()

    def blob_xml_to_array(self):
        """
        Convert the "BLOB" register in the device specific config and add to the 'xml' array

        product: self.board_xml
        specification: self.specification_xml['xml']
        """

        self.logger.debug("Parsing the blob:")

        # Find all blobs in the BLOB register
        blobs = self.config_xml.findall("./register[@name='BLOB']/blob")

        blob_specification = self.specification_xml['xml'].find("./registers/register[@type='BLOB']")

        # Get register parameters from the specification
        blob_register = self.specification_xml['xml'].find("./registers/register[@name='BLOB']")
        name = blob_register.attrib['name']
        offset = self.string_value_to_int(blob_register.attrib['offset'])
        size = self.string_value_to_int(blob_register.attrib['size'])

        if blobs == []:
            # No data in the blob section
            self.data_end['xml'] = offset
        else:
            # Decode each blob one-by-one
            for blob in blobs:
                blob_array = self._get_blob_array(blob, blob_specification)

                data_length = len(blob_array)

                if data_length > size:
                    raise PydebuggerconfigError("Trying to put {} bytes of data in {} with size {}."
                                                .format(data_length, name, size))

                address = 0
                # Put data in the config array
                for i in range(data_length):
                    address = offset + i
                    if self.data_array['xml'][address] != 0:
                        self.logger.error("Overwrite detected at address 0x%X", address)
                    self.data_array['xml'][address] = blob_array[i]

                self.data_end['xml'] = address

    def _get_blob_array(self, blob, blob_specification):
        token = blob.find("./token").text

        self.logger.debug("Found a %s token in the blob", token)

        # Find the ENUM value for the token
        token_value = blob_specification.find(".//token/value[@name='{}']".format(token)).attrib['value']

        blob_array = []

        if token == "list".upper():
            entries_array = self._get_list_token_entries(token, blob, blob_specification)
        else:
            raise PydebuggerconfigError("Unknown token found in blob")

        # How many data entries do we have?
        number_entries = len(entries_array)

        # Calculate the offset to each data entry
        offsets = []
        addr = 2 + number_entries * 2
        for i in range(0, number_entries):
            offsets.append(addr)
            addr += len(entries_array[i])

        # Build the blob array
        blob_array.extend(self.value_to_array_8bit(token_value, 1))
        blob_array.extend(self.value_to_array_8bit(len(entries_array), 1))
        for item in offsets:
            blob_array.extend(self.value_to_array_8bit(item, 2))
        for item in entries_array:
            blob_array.extend(item)

        return blob_array

    def _get_list_token_entries(self, token, blob, blob_specification):
        # Fetch the specification for this token
        token_specification = blob_specification.find(".//{}".format(token.lower()))

        entries_array = []
        # Find all entries
        for entry in blob.findall("./entry"):
            entry_type = entry.find("./type")

            self.logger.debug("Found a %s entry in the list", entry_type.text)

            # Find the specification for the entry type
            pat = ".//*[@type='{}']".format(entry_type.text)
            specification = blob_specification.find(pat)

            entry_array = []

            # Find the entry value and add it to the array (D or S)
            entry_value = token_specification.find("./entry/type/value[@name='{}']"
                                                   .format(entry_type.text)).attrib['value']
            entry_array.extend(self.value_to_array_8bit(entry_value, 1))

            # Some hard-coding here:
            if entry_type.text == "SCRIPT":
                entry_array.extend(self.script_xml_to_array(entry))
            elif entry_type.text == "PRIMITIVE_SEQUENCE":
                entry_array.extend(self.primitive_xml_to_array(entry))
            elif entry_type.text.startswith("D_"):
                entry_array.extend(self.device_context_xml_to_array(entry, specification))
            else:
                raise PydebuggerconfigError("Unknown entry type found in list blob")

            padding = len(entry_array) % 4
            entry_array.extend([0] * padding)

            entries_array.append(entry_array)

        return entries_array

    def device_context_xml_to_array(self, entry, specification):
        """
        Convert xml device data to list ready for programming

        :param entry: XML entry
        :type entry: str
        :param specification: XML specification
        :type specification: str
        :return: list of byte values
        :rtype: list[byte]
        :raises:
            PydebuggerconfigError: if there is a mismatch between the data and the specification
        """
        # Find the largest offset (and size) in the device context
        # Create an array with 0's that spans the entire memory range of this entry
        max_offset = 0
        max_offset_size = 0
        for register in specification:
            f_offset = self.string_value_to_int(register.attrib['offset'])
            if f_offset > max_offset:
                max_offset = f_offset
                max_offset_size = self.string_value_to_int(register.attrib['size'])
        array = [0]*(max_offset + max_offset_size)

        # Find data in the entry for every register in the specification
        for register in specification:
            data = entry.findall("./data[@type='{}']".format(register.tag))
            if len(data) != 1:
                raise PydebuggerconfigError("{} device context entries for {} found, there must be exactly 1"
                                            .format(len(data), register.tag))

            value = self.string_value_to_int(data[0].text)
            size = self.string_value_to_int(register.attrib['size'])
            offset = self.string_value_to_int(register.attrib['offset'])

            if self.verify_blob_register(value, size):
                # Insert the data into the array
                array[offset:offset+size] = self.value_to_array_8bit(value, size)
            else:
                raise PydebuggerconfigError("Invalid device context entry '{}' found".format(register.tag))

        # The ID register is not used in device context, initialize to 0
        preamble = [0]

        # Add the number of data bytes in the device context
        num = len(array)
        if not self.verify_blob_register(num, 2):
            raise PydebuggerconfigError("This device context is too long")

        preamble.extend(self.value_to_array_8bit(num, 2))
        self.logger.debug("Device context is %d bytes long", num)

        # Join the preamble and data
        preamble.extend(array)

        return preamble

    def script_xml_to_array(self, entry):
        """
        Convert a script entry to an array ready for programming

        :param entry: XML entry with script data
        :type entry: str
        :return: list of byte values
        :rtype: list[byte]
        :raises:
            PydebuggerconfigError: if the entry data is invalid
        """
        array = []

        # Find and add the script id
        id_number = entry.findall('id')

        if len(id_number) != 1:
            raise PydebuggerconfigError("Found {} ID registers in script, only 1 is allowed".format(len(id_number)))

        id_value = self.string_value_to_int(id_number[0].text)
        if self.verify_blob_register(id_value, 1):
            array.append(id_value)

        # Find all the data
        data = entry.findall('data')

        # Add the data length
        data_number = len(data)
        if not self.verify_blob_register(data_number, 2):
            raise PydebuggerconfigError("This script is too long")
        array.extend(self.value_to_array_8bit(data_number, 2))

        # Add the script data
        for value in data:
            value = self.string_value_to_int(value.text)
            if self.verify_blob_register(value, 1):
                array.append(value)

        return array

    def primitive_xml_to_array(self, entry):
        """
        Convert a primitive entry to an array ready for programming

        :param entry: XML entry containing programming primitives data
        :type entry: str
        :return: list of byte values
        :rtype: list[byte]
        :raises:
            PydebuggerconfigError: if entry data is invalid
        """
        array = []

        # Find and add the script id
        id_number = entry.findall('id')

        if len(id_number) != 1:
            raise PydebuggerconfigError("Found {} ID registers in script, only 1 is allowed".format(len(id_number)))

        id_value = self.string_value_to_int(id_number[0].text)
        if self.verify_blob_register(id_value, 1):
            array.append(id_value)

        # Find the script data, split the string into a list
        script = entry.find('data').text.split(',')

        # Scrub whitespace, \r, and \n
        for i, data in enumerate(script):
            script[i] = data.replace(" ", "").replace("\n", "").replace("\r", "")

        # Add the script length
        script_length = len(script)
        if not self.verify_blob_register(script_length, 2):
            raise PydebuggerconfigError("This script is too long")
        array.extend(self.value_to_array_8bit(script_length, 2))

        # Add the script data
        for data in script:
            value = self.string_value_to_int(data)
            if self.verify_blob_register(value, 1):
                array.append(value)

        return array

    def verify_blob_register(self, data, size):
        """
        Verifies that the data fits in a list of [size] bytes

        :param data: string representing an int
        :type data: str
        :param size: number of bytes in the register
        :type size: int
        :return: True if the data is valid for the register, False if it is too big
        :rtype: bool
        """
        valid = False
        number = self.string_value_to_int(data)

        if number > 2 ** (size * 8) - 1:
            self.logger.error("Number %d is too big for a register of size %d", data, size)
        else:
            valid = True

        return valid

    def calculate_checksum(self):
        """
        Calculate the CRC-CCIT checksum of all the data in the configuration
        """
        self.logger.debug("Calculating data length and CRC-CCIT")
        # Fetch parameters of the length and checksum registers
        length_register = self.specification_xml['xml'].find("./registers/register[@name='CONTENT_LENGTH']")
        # Get register parameters from the specification
        length_offset = self.string_value_to_int(length_register.attrib['offset'])
        length_size = self.string_value_to_int(length_register.attrib['size'])

        # The checksum register contains the checksum of all data after itself.
        checksum_register = self.specification_xml['xml'].find("./registers/register[@name='CONTENT_CHECKSUM']")
        # Get register parameters from the specification
        checksum_offset = self.string_value_to_int(checksum_register.attrib['offset'])
        checksum_size = self.string_value_to_int(checksum_register.attrib['size'])

        data_start = checksum_offset + checksum_size

        # zero-indexed end address and remove the first registers
        data_length = self.value_to_array_8bit(self.data_end['xml'] + 1 - data_start, length_size)
        self.logger.debug("We have %d bytes of data", self.array_8bit_to_value(data_length))

        # Add the length to the config array
        for i, byte in enumerate(data_length, 0):
            self.data_array['xml'][length_offset+i] = byte

        data_sum = sum(self.data_array['xml'][data_start:])
        self.logger.debug("The sum of the config data is %s", data_sum)

        # Calculate the CRC value
        crc = self.crc("{}".format(data_sum).encode("utf-8"))
        self.logger.debug("Calculated CRC-CCIT (0xFFFF): %04X", crc)

        # Add the CRC to the config array
        crc_array = self.value_to_array_8bit(crc, checksum_size)
        for i, byte in enumerate(crc_array, 0):
            self.data_array['xml'][checksum_offset+i] = byte

    def config_program(self, source='xml', factory=False):
        """
        Programs the device configuration

        :param source: data source, either 'xml' or 'board'
        :type source: str
        :param factory: Not used, there is no factory section for device config
        :type factory: bool
        """
        if factory:
            raise NotImplementedError("Device config has no factory section")

        # Check that a tool is connected
        self.transport_check()

        # Write the configuration data
        self.protocol.write_device_data_block(self.data_array[source])

    def config_read_from_board(self, source='board', factory=False):
        """
        Reads device configuration from a connected kit

        :param source: where to store the data, either 'board' or 'xml'
        :type source: str
        :param factory: Not used, there is no factory section for device config
        :type factory: bool
        """
        if factory:
            raise NotImplementedError("Device config has no factory section")

        # Check that a tool is connected
        self.transport_check()

        # Read the configuration data
        self.logger.info("Reading configuration from board:")
        self.data_array[source] = self.protocol.read_device_data_block()

        # Version numbers are always at the top:
        major = self.data_array[source][0]
        minor = self.data_array[source][1]
        build = self.array_8bit_to_value(self.data_array[source][2:4])

        self.logger.info("Read version: %d.%d.%d", major, minor, build)

        self.major[source] = major
        self.minor[source] = minor
        self.build[source] = build

        # Automatically open a specification xml
        self.specification_open(source)

    def config_array_create_empty(self, source):
        """
        Creates an empty config array in self.config_data[source]

        :param source: either 'xml' or 'board'
        :type source: str
        """
        self.data_array[source] = configprotocol.create_blank_device_data_block()

    def config_array_print(self, source):
        """
        Decode a device config array with self.specification_xml[source]

        Additional code to decode the device BLOB
        :param source: either 'xml' or 'board'
        :type source: str
        :returns Human-readable string representation of the config
        :rtype: str
        """

        # Call the base class implementation
        string = BaseConfig.config_array_print(self, source)

        # https://jira.microchip.com/browse/DSG-2199
        self.logger.info("Decoding of the BLOB not implemented")

        return string
