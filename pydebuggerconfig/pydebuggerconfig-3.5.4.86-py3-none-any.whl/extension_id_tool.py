"""
Command line tool for reading and writing Xplained Pro extension ID, and reading
the EDBG extra kit info
"""

# Add support for Python 3 style printing
from __future__ import print_function

import sys
import os
import argparse
import logging
from logging.config import dictConfig
import textwrap
import yaml

from appdirs import user_log_dir
from yaml.scanner import ScannerError

# Import the main ID module which provedes the low level communication
from . import extension_id_tool_main

def setup_logging(user_requested_level=logging.WARNING, default_path='logging.yaml',
                  env_key='MICROCHIP_PYTHONTOOLS_CONFIG'):
    """
    Setup logging configuration for this CLI
    """
    # Logging config YAML file can be specified via environment variable
    value = os.getenv(env_key, None)
    if value:
        path = value
    else:
        # Otherwise use the one shipped with this application
        path = os.path.join(os.path.dirname(__file__), default_path)
    # Load the YAML if possible
    if os.path.exists(path):
        try:
            with open(path, 'rt') as file:
                # Load logging configfile from yaml
                configfile = yaml.safe_load(file)
                # File logging goes to user log directory under Microchip/modulename
                logdir = user_log_dir(__name__, "Microchip")
                # Create it if it does not exist
                os.makedirs(logdir, exist_ok=True)
                # Look through all handlers, and prepend log directory to redirect all file loggers
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        configfile['handlers'][handler]['filename'] = os.path.join(
                            logdir, configfile['handlers'][handler]['filename'])

                # Console logging takes granularity argument from CLI user
                configfile['handlers']['console']['level'] = user_requested_level
                # Root logger must be the most verbose of the ALL YAML configurations and the CLI user argument
                most_verbose_logging = min(user_requested_level, getattr(logging, configfile['root']['level']))
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        level = getattr(logging, configfile['handlers'][handler]['level'])
                        most_verbose_logging = min(most_verbose_logging, level)
                configfile['root']['level'] = most_verbose_logging
            dictConfig(configfile)
            return
        except ScannerError:
            # Error while parsing YAML
            print("Error parsing logging config file '{}'".format(path))
        except KeyError as keyerror:
            # Error looking for custom fields in YAML
            print("Key {} not found in logging config file".format(keyerror))
    else:
        # Config specified by environment variable not found
        print("Unable to open logging config file '{}'".format(path))

    # If all else fails, revert to basic logging at specified level for this application
    print("Reverting to basic logging.")
    logging.basicConfig(level=user_requested_level)

def main():
    """
    Entrypoint for the ID command line tool

    Configures the CLI and parses the arguments
    """

    # Shared switches.  These are inherited by subcommands (and root) using parents=[]
    common_argument_parser = argparse.ArgumentParser(add_help=False)
    common_argument_parser.add_argument("-v", "--verbose",
                                        default="warning",
                                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                                        help="Logging verbosity/severity level")

    parser = argparse.ArgumentParser(
        parents=[common_argument_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
    Xplained Pro ID tool

    Basic actions:
        - read-id:               read Xplained Pro extension ID
        - write-id:              write Xplained Pro extension ID
        - read-edbg-extra-info:  read the Xplained Pro extra info flash page
        """), epilog=textwrap.dedent("""\
    Usage examples:
        Read the kit info:
        - extension-id-tool read-edbg-extra-info -v info
        - extension-id-tool read-id -ext 3
        - extension-id-tool write-id -ext 2 -m Microchip -n OLED Xplained Pro -r 01
                              -cs 0110100101101000 -vmin 3000 -vmax 3600 -current 10
    """))

    subparsers = parser.add_subparsers()

    write_id_parser = subparsers.add_parser("write-id",
                                            parents=[common_argument_parser],
                                            help="write Xplained Pro extension ID")
    read_id_parser = subparsers.add_parser("read-id",
                                           parents=[common_argument_parser],
                                           help="read Xplained Pro extension ID")
    edbg_extra_info = subparsers.add_parser("read-edbg-extra-info",
                                            parents=[common_argument_parser],
                                            help="read the Xplained Pro extra info flash page")

    # Write ID parser arguments
    write_id_parser.add_argument("-ext", "--extension",
                                 required=True, help="Extension number", type=int)

    write_id_parser.add_argument("-m", "--manufacturer",
                                 required=True, help="Extension manufacturer name", type=str)

    write_id_parser.add_argument("-n", "--name",
                                 required=True, help="Extension name", type=str)

    write_id_parser.add_argument("-r", "--revision",
                                 required=True, help="Revision number of the extension", type=str)

    write_id_parser.add_argument("-cs", "--config-serial-number",
                                 required=True, help="Serial number to be written to extension", type=str)

    write_id_parser.add_argument("-vmin", "--vmin",
                                 required=True, help="Extension minimum operating voltage [mV]", type=int)

    write_id_parser.add_argument("-vmax", "--vmax",
                                 required=True, help="Extension maximum operating voltage [mV]", type=int)

    write_id_parser.add_argument("-current", "--current",
                                 required=True, help="Extension current consumption [mA]", type=int)

    # Read ID parser arguments
    read_id_parser.add_argument("-ext", "--extension",
                                required=True, help="Extension header number of the connected ID device", type=int)

    # This is for knowing which parser has been invoked
    write_id_parser.set_defaults(action="write_id")
    read_id_parser.set_defaults(action="read_id")
    edbg_extra_info.set_defaults(action="read_edbg_extra_info")

    arguments = parser.parse_args()

    if len(sys.argv) <= 1:
        print("No valid argument given (choose from 'write-id', 'read-id', 'read-edbg-extra-info')")
        sys.exit(1)

    # Setup logging
    setup_logging(user_requested_level=getattr(logging, arguments.verbose.upper()))

    tool = extension_id_tool_main.extension_id_tool()

    # Check which function to call
    if arguments.action == "write_id":
        tool.write_id(arguments.extension, arguments.manufacturer, arguments.name,
                      arguments.revision, arguments.config_serial_number, arguments.vmin,
                      arguments.vmax, arguments.current)

    elif arguments.action == "read_id":
        tool.read_id(arguments.extension)

    elif arguments.action == "read_edbg_extra_info":
        tool.read_edbg_extra_info()

if __name__ == "__main__":
    sys.exit(main())
