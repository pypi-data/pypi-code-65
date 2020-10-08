"""
Command line utility for reading/writing kit ID and kit info
"""

import logging

# Include pyedbglib dependencies
from pyedbglib.hidtransport.hidtransportfactory import hid_transport
from pyedbglib.protocols.edbgprotocol import EdbgProtocol as edbg_protocol
from pyedbglib.protocols.avrcmsisdap import AvrCommandError


class extension_id_tool():
    """
    Class for reading and writing extension ID and kit info flash page
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Try to connect to the transport layer
        self.transport = hid_transport()

        # This must allways be defined in the class since class functions can
        # be called even though the EDBG connection fails
        self.edbg_connected = None

        # Try to connect to EDBG
        if self.transport.connect():
            # Initialize the EDGB interface
            self.edbg = edbg_protocol(self.transport)
            self.edbg_connected = True
        else:
            self.edbg_connected = False

    def __del__(self):
        # Dissconnect the transport layer
        if self.edbg_connected:
            self.transport.disconnect()

    def read_id(self, extension):
        """
        Reads and prints the kit info from the ID chip

        :param extension: extension number
        """
        if not self.edbg_connected:
            self.logger.error("EDBG is not connected")
            return
        if extension == 0:
            self.logger.error("Extension number can not be zero")
            return

        # Refresh the ID chip and read the ID data
        self.edbg.refresh_id_chip()
        try:
            id_data = self.edbg.read_id_chip(extension)
        except AvrCommandError:
            self.logger.error("AVR command error")

        # Try to print the ID data
        if not self.print_id(id_data):
            self.logger.warning("Invalid ID data received - check that a valid extension number is specified!")
            return

    def write_id(self, extension, manufacturer, name, revision, serialnumber, vmin, vmax, current):
        """
        Writes the kit info to the ID chip

        :param extension: extension number
        :param manufacturer: manufacturer string
        :param name: name of the extension string
        :param revision: revision number
        :param serialnumber: number string representation of the serial number
        :param vmin: minimum voltage supported
        :param vmax: maximum voltage supported
        :param current: supply current
        """
        if not self.edbg_connected:
            self.logger.error("EDBG is not connected")
            return
        if extension == 0:
            self.logger.error("Extension number can not be zero")
            return

        # Try to parse the data first
        raw_id = self.encode_id(manufacturer, name, revision, serialnumber,
                                vmin, vmax, current)

        if not raw_id:
            self.logger.error("Invalid ID data")
            return
        if self.logger.level <= logging.INFO:
            self.print_id(raw_id)

        # Refresh the ID chip and write the ID data
        self.edbg.refresh_id_chip()
        status_code = self.edbg.program_id_chip(extension, raw_id)
        self.print_status_code(status_code)

        if status_code == 0xe7:
            self.logger.warning("Have you specified the correct extension number?")

    def read_edbg_extra_info(self):
        """
        Read and print the kit info flash page
        """
        if not self.edbg_connected:
            self.logger.error("EDBG not connected")
            return

        kit_info = self.edbg.read_edbg_extra_info()
        if not kit_info:
            self.logger.error("Unable to read kit info")
            return

        # The kit info is a flash page. The base address is set to zero just for
        # visual pleasure. This has nothing to to with the actual page offset
        print("Printing kit info using relative address:")
        self.print_flash_page(kit_info, 0)

    def print_flash_page(self, data, start_address):
        """
        Prints the memory representation of `data` virtually starting at the
        given start address.  If the data is not 512 bytes, it prints a warning.

        :param data: the data page to be printed
        :param start_address: start address of the page.  Set to `0` for a nice
                              print if the start address does not matter
        """
        if len(data) != 512:
            self.logger.warning("Non complete page received")

        for i in range(len(data)):
            # Print the address on the start of the line
            if (i % 8) == 0:
                print("0x{:04x}: ".format(start_address), end=" ")

            print("0x{:02x}".format(data[i]), end=" ")
            if ((i + 1) % 8) == 0:
                print()
            start_address += 1

    def print_id(self, data):
        """
        Decodes and prints the ID data from the extension

        :param data: list with 64 bytes
        :return True if the data is correct, false if not
        """
        # If the data is all zeros the extension is most likely not connected
        if all(i == 0 for i in data):
            self.logger.error("Kit ID is blank")
            return False

        string_info = [None] * 4
        min_voltage = None
        max_voltage = None
        current = None

        # These are used to decode the first four string fragments
        string_count = 0
        string_fragment = ""

        # String part of the ID message cannot be longer than 58 characters. The
        # data list contains four custom sized strings separated by a null
        # terminating character
        for i in range(58):
            if string_count >= 4:
                break
            if not data[i]:
                # This will be used to hold the four strings
                string_info[string_count] = string_fragment
                string_count += 1
                string_fragment = ""
            else:
                string_fragment += chr(data[i])

        if string_count != 4:
            return False

        min_voltage = (data[58] << 8) + data[59]
        max_voltage = (data[60] << 8) + data[61]
        current = (data[62] << 8) + data[63]

        print("Manufacturer:\t", string_info[0])
        print("Name:\t\t", string_info[1])
        print("Revision:\t", string_info[2])
        print("Serial number:\t", string_info[3])
        print("Min voltage:\t", min_voltage, "mV")
        print("Max voltage:\t", max_voltage, "mV")
        print("Current:\t", current, "mA")
        return True

    def encode_id(self, manufacturer, name, revision, serialnumber, vmin, vmax, current):
        """
        Encodes the given ID data into a 64 byte string

        :param manufacturer: manufacturer string
        :param name: name of the extension string
        :param serialnumber: number string representation of the serial number
        :param revision: revision number
        :param vmin: minimum voltage supported
        :param vmax: maximum voltage supported
        :param current: supply current
        :return 64-byte encoded ID data if success, else False
        """
        # Check that no arguments are None
        if not all(arg is not None for arg in [manufacturer, name, serialnumber, revision, vmin, vmax, current]):
            self.logger.error("Please give a value to all required arguments")
            return False

        # Check that the string section does not exceed the maximum size
        if (len(manufacturer) + len(name) + len(serialnumber) + len(revision)) > 54:
            self.logger.error("Manufacturer, name, serial number and revision exceeds 54 characters...")
            return False

        raw_id_data = []
        raw_id_data.extend(manufacturer + "\0")
        raw_id_data.extend(name + "\0")
        raw_id_data.extend(revision + "\0")
        raw_id_data.extend(serialnumber + "\0")

        # Convert ASCII data to int
        for i in range(len(raw_id_data)):
            raw_id_data[i] = ord(raw_id_data[i])

        # Extend the string part to exactly 58 byte padded with 0xFF
        for i in range(58 - len(raw_id_data)):
            raw_id_data.append(int(0xFF))

        if vmax < vmin:
            self.logger.error("vmin cannot be greater than vmax")
            return False

        # Append voltage and current information
        raw_id_data.append((vmin & 0xFF00) >> 8)
        raw_id_data.append((vmin & 0x00FF))
        raw_id_data.append((vmax & 0xFF00) >> 8)
        raw_id_data.append((vmax & 0x00FF))
        raw_id_data.append((current & 0xFF00) >> 8)
        raw_id_data.append((current & 0x00FF))

        return raw_id_data

    def print_status_code(self, status_code):
        """
        Prints the string representation of the status code returned from
        the write kit ID functions

        :param status_code: a one-byte status code
        """
        id_codes = {0x00: "Operation completed successfully"}
        id_codes[0xD2] = "Parsing error"
        id_codes[0xD3] = "Command failed"
        id_codes[0xD4] = "CRC error"
        id_codes[0xE0] = "Operation failed due to incorrect condition/state"
        id_codes[0xE2] = "Invalid argument (out of range, null pointer etc.)"
        id_codes[0xE4] = "Count value is out of range or greater than buffer size"
        id_codes[0xE5] = "Incorrect CRC received"
        id_codes[0xE6] = "Timed out while waiting for response. Number or received bytes is > 0"
        id_codes[0xE7] = "Not an error while the Command layer is polling for a command response"
        id_codes[0xE8] = "Re-synchronization succeeded, but only after generating a Wake-up"
        id_codes[0xF0] = "Communication with device failed. Same as in hardware dependent modules"
        id_codes[0xF1] = "Timed out while waiting for response. Number of bytes received is 0"
        id_codes[0xFA] = "ID data locked"
        id_codes[0xFB] = "ID config locked"
        id_codes[0xFC] = "ID invalid slot"
        id_codes[0xFD] = "ID data parsing error"
        id_codes[0xFE] = "ID data not equal"

        print("Status: " + hex(status_code) + " - " + id_codes[status_code])
