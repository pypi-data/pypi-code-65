"""
Board configuration class
"""
from __future__ import print_function
import glob
import datetime
from logging import getLogger
from packaging import version

# pyedbglib dependencies
import pyedbglib.protocols.configprotocol as configprotocol

from .baseconfig import BaseConfig
from .pydebuggerconfig_errors import PydebuggerconfigError


class BoardConfig(BaseConfig):
    """
    Class to work with board configuration data for the PKOB nano (nEDBG) debugger from Microchip
    """

    PRETTY_NAME = "Board Configuration"

    XML_ROOT_NAME = "configuration"

    SPECIFICATION_NAME = "board_config_defines"

    def __init__(self):
        BaseConfig.__init__(self)

        # Logger object
        self.logger = getLogger(__name__)

    def specification_update(self, target_version=None):
        """
        Upgrades the board config version to latest.

        Only backward compatible updates are done, i.e. only minor version updates.  Its the caller's obligation to
        commit changes.
        :param target_version: specific version to update to.  None updates to latest.  Currently this parameter is
            not supported
        :type target_version: str
        :return: (updated, version) where updated is True if an update was made, False otherwise and version is the
            current config version after the update
        :rtype: (bool, str)
        """
        if target_version is not None:
            # https://jira.microchip.com/browse/DSG-2201
            raise NotImplementedError("update spec to specific version is currently not supported")

        # Look in the specs folder for matching candidates
        path = self.SPECIFICATION_FOLDER
        filename = 'board_config_defines'
        ext = 'xml'

        # Use the board's current major version as a reference
        current_version = '{0:d}.{1:d}.{2:d}'.format(self.major['board'], self.minor['board'], self.build['board'])
        self.logger.info("Current version is %s", current_version)
        major = self.major['board']

        self.logger.debug("Looking for latest specification version")
        files = glob.glob('{}//{}-{}*.{}'.format(path, filename, major, ext))

        # Parse all candidates to find the latest version
        latest = current_version
        for spec_file in files:
            # Split out the version
            spec_version = spec_file.split('{}-'.format(filename))[1].split('.{}'.format(ext))[0]
            # And the major part thereof
            spec_major = spec_version.split('.')[0]
            # Only if major matches will this be a candidate
            if int(spec_major) == int(major):
                # And only if its an upgrade
                self.logger.debug("Found specification version %s", spec_version)
                if version.parse(spec_version) > version.parse(latest):
                    latest = spec_version

        # Check if things are already up to date
        if latest == current_version:
            # All good - nothing to do here
            self.logger.debug("Board config specification is up to date.")
            return (False, current_version)

        self.logger.info("Latest specification version with matching major version is %s", latest)

        # Repopulate registers.  Leave it up to the caller to commit changes.
        new_version = latest.split(".")
        self.register_set("CONFIG_FORMAT_MINOR", int(new_version[1]), source='board')
        self.register_set("CONFIG_FORMAT_BUILD", int(new_version[2]), source='board')
        self.logger.info("Updated version is %s", latest)
        return (True, latest)

    def config_program(self, source='xml', factory=False):
        """
        Programs the board configuration with the chosen transport

        :param source: either 'xml' or 'board'
        :type source: str
        :param factory: if True the factory section will be written, if False the user section will be written
        :type factory: bool
        """
        # Check that a tool is connected
        self.transport_check()

        # Replace the value in the "DATE" register with the current date
        self.date_set(source)

        # Write the configuration data
        self.protocol.write_config_block(self.data_array[source], factory=factory)

    def config_read_from_board(self, source='board', factory=False):
        """
        Read board configuration from a kit

        :param source: either 'board' or 'xml'
        :type source: str
        :param factory: if True the factory section will be read, if False the user section will be read
        :type factory: bool
        """
        # Check that a tool is connected
        self.transport_check()

        self.logger.info("Reading configuration from board (factory=%s):", factory)

        # Read config from the board
        self.data_array[source] = self.protocol.read_config_block(factory)

        # Version numbers are located at the start of the configuration:
        major = self.data_array[source][0]
        minor = self.data_array[source][1]
        build = self.array_8bit_to_value(self.data_array[source][2:4])

        self.logger.info("Read version: %s.%s.%s", major, minor, build)
        if major == 0xFF and minor == 0xFF and build == 0xFFFF:
            self.logger.error("Board contains suspiciously blank version.")

        self.major[source] = major
        self.minor[source] = minor
        self.build[source] = build

        # Automatically open a specification xml
        self.specification_open(source)

    def date_set(self, source='xml'):
        """
        Replace the value of the DATE register with today

        :param source: either 'xml' or 'board'
        :type source: str
        :raises:
            PydebuggerconfigError: if the date format is incorrect
        """
        # Fetch the current date in YYYYMMDD format
        date = datetime.datetime.now().strftime("%Y%m%d")

        if len(date) != 8:
            raise PydebuggerconfigError("DATE string {} does not fit in the format YYYYMMDD".format(date))

        self.register_set("DATE", date, source)

    def serial_set(self, serial):
        """
        Replace the value of the serial number register

        :param serial: USB serial number (must be exactly 20 ASCII characters)
        :type serial: str
        :raises:
            PydebuggerconfigError: if the serial number is not exactly 20 characters
        """
        if len(serial) != 20:
            msg = "Serial number must be exactly {} characters, '{}' is {} characters long"\
                .format(20, serial, len(serial))
            raise PydebuggerconfigError(msg)

        self.register_set("SERNUM", serial, source='xml')

    def config_array_create_empty(self, source):
        """
        Creates an empty config array in self.config_data[source]

        :param source: either 'xml' pr 'board'
        :type source: str
        """
        self.data_array[source] = configprotocol.create_blank_config_block()
