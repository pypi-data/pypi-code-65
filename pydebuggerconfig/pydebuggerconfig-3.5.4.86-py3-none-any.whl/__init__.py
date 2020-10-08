"""
Python Debugger/Kit Configuration utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pydebuggerconfig is a utility for reading and writing the configuration data in the PKOB nano (nEDBG) on-board
debuggers.

pydebuggerconfig can be used as a library using its "backend API". For example:
Instantiate backend (if more than one kit is connected a serial number must be provided as parameter to the Backend
constructor):
    >>> from pydebuggerconfig.backend import Backend
    >>> pb = Backend()

Write board configuration data to a kit, preserving KITNAME and setting custom USB serial number
    >>> board_config_string = pb.write_board_config("board-configs/ATmega4809-CNANO.xml",
                                                     serial_number="MYSERIALNUMBER012345",
                                                     preserve=['KITNAME'])
    >>> print("Written board config to kit:")
    >>> print(board_config_string)

Write device configuration data to a kit
    >>> device_config_string = pb.write_device_config("device-configs/ATmega4809-device-blob.xml)
    >>> print("Written device config to kit:")
    >>> print(device_config_string)

Update the kit name and serial number of a kit:
    >>> registers = {'KITNAME': 'My new kitname', 'SERNUM': 'MYNEWSERIAL012345678'}
    >>> pb.replace(registers)

Read out and print board configuration data from a kit:
    >>> board_config_string = pb.read_board_config_as_string("board-configs/ATmega4809-CNANO.xml")
    >>> print("Board config from kit:")
    >>> print(board_config_string)

Read out and print device configuration data from a kit:
    >>> device_config_string = pb.read_device_config_as_string()
    >>> print("Device config from kit:")
    >>> print(device_config_string)

Print the pydebuggerconfig package version
    >>> from pydebuggerconfig.version import VERSION as pydebuggerconfig_version
    >>> print("pydebuggerconfig version {}".format(pydebuggerconfig_version))

In addition, the CLI-backend API is versioned for convenience:
    >>> print("pydebuggerconfig backend API version: {}".format(pb.get_api_version()))

Configuration XML files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The actual configuration data to be programmed into the debugger's configuration space is stored in XML files,
one file for the data concerning the debugger and kit itself and one file with data concerning the target device.
The board related files are stored in the pydebuggerconfig/board-configs folder and the device specific files
are stored in the pydebuggerconfig/device-configs folder.  Pydebuggerconfig also supports XML files stored in
other folders by providing the full path to the files.

The specifications for the config XML files are stored in the pydebuggerconfig/config-specification folder.
Each configuration file specifies which specification version to be used by the version registers in the XML file.
These are called CONFIG_FORMAT_MAJOR, CONFIG_FORMAT_MINOR and CONFIG_FORMAT_BUILD for board configuration files and
DEVICE_CONFIG_MAJOR, DEVICE_CONFIG_MINOR and DEVICE_CONFIG_BUILD for device configuration files.  The version of
the specification files are given by the file name.  Example:
A board config XML file with the following version registers
    <register name="CONFIG_FORMAT_MAJOR" value="1"/>
    <register name="CONFIG_FORMAT_MINOR" value="5"/>
    <register name="CONFIG_FORMAT_BUILD" value="47"/>
will refer to specification files
    board_config_defines-1.5.47.xml and board_config_defines-1.5.47.xsd


Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pydebuggerconfig depends on pyedbglib for its transport protocol.
pyedbglib requires a USB transport library like libusb.  See pyedbglib package for more information.

Supported tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pydebuggerconfig only supports PKOB nano (nEDBG) debuggers.  These are typically found on Curiosity Nano kits
"""
