"""
Command line utility for reading/writing/modifying board configuration
"""
# Python 3 compatibility for Python 2
from __future__ import print_function

import sys
import os
import logging
import argparse
from logging.config import dictConfig
import yaml

from appdirs import user_log_dir
from yaml.scanner import ScannerError

from . import pydebuggerconfig_main

TOOL = 'nEDBG CMSIS-DAP'

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
    Entrypoint for installable CLI
    """
    epilog = ("actions:\n"
              "  read:                 read out the config from a kit\n"
              "  write:                write the specified config XML file(s) to a kit\n"
              "  show:                 display a kit's config in human-readable form on screen\n"
              "  verify:               check that the specified config XML is programmed on a kit\n"
              "  replace:              modify a particular config register on a kit leaving the rest unchanged\n"
              "  restore:              copy a kit's factory config to user config\n"
              "  version-update:       update the version registers in a kit to allow new registers to be supported\n"
              "  generate-hex:         generate an Intel-hex file of a config XML\n")

    parser = argparse.ArgumentParser(description="Provides access to PKOB nano on-board debugger configuration data",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=epilog
                                     )

    parser.add_argument("action",
                        help="action to perform",
                        # This makes action argument optional only if version (-V) argument is given
                        nargs="?" if "-V" in sys.argv or "--version" in sys.argv  \
                        or "-R" in sys.argv or "--release-info" in sys.argv else None,
                        default="read",
                        choices=['read',
                                 'write',
                                 'show',
                                 'verify',
                                 'replace',
                                 'restore',
                                 'version-update',
                                 'generate-hex'])

    parser.add_argument("-s", "--serialnumber",
                        default='',
                        help="USB serial number of the unit to connect to. \n"
                        "Substring matching on end of serial number is supported.\n"
                        "Note that this is the serial number of the unit before updating config and\n"
                        "must not be confused with the -s/--serialnumber option which is the serial\n"
                        "number to write to the config\n")

    parser.add_argument("-b", "--board",
                        help="Board configuration xml")

    parser.add_argument("-d", "--device",
                        help="Device configuration xml")

    parser.add_argument("-cs", "--config-serialnumber",
                        help="Board serial number to program (20 ASCII characters)")

    parser.add_argument("-p", "--preserve",
                        nargs='+',
                        help="Preserve parameters when writing board config\n"
                             "Example: pydebuggerconfig write -p KITNAME SERNUM -b board_config.xml")

    parser.add_argument("-r", "--register",
                        nargs='+',
                        help="Register to replace in board user config (factory config not affected).\n"
                             "Example: pydebuggerconfig replace -r KITNAME=\"My kitname\" "
                             "SERNUM=01234567890123456789\n")

    parser.add_argument("-fa", "--factory",
                        action="store_true",
                        help="read/write the factory area of the board config")

    parser.add_argument("-v", "--verbose",
                        default="warning",
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help="Logging verbosity/severity level")

    parser.add_argument("-V", "--version",
                        help="Print pydebuggerconfig version number and exit",
                        action="store_true")

    parser.add_argument("-R", "--release-info", action="store_true",
                        help="Print pydebuggerconfig release details and exit")

    arguments = parser.parse_args()

    # Setup logging
    setup_logging(user_requested_level=getattr(logging, arguments.verbose.upper()))

    return pydebuggerconfig_main.pydebuggerconfig(arguments)


if __name__ == '__main__':
    sys.exit(main())
