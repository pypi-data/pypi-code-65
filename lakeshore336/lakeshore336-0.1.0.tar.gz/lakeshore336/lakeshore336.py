""" Logging and control module for the Lakeshore 336
Temperature Controller. The module manages a
:class:`~Daemon.Daemon` object over TCP communication.
"""

# Imports
from sys import argv
from configparser import Error as ConfigError
from argparse import ArgumentParser, Namespace

# Third party
from zc.lockfile import LockError
from lab_utils.socket_comm import Client
from lab_utils.custom_logging import configure_logging, getLogger

# Local packages
from lakeshore336.Daemon import Daemon
from lakeshore336.__project__ import (
    __documentation__ as docs_url,
    __module_name__ as module,
    __description__ as prog_desc,
)


def lakeshore336():
    """The main routine. It parses the input argument and acts accordingly."""

    # The argument parser
    ap = ArgumentParser(
        prog=module,
        description=prog_desc,
        add_help=True,
        epilog='Check out the package documentation for more information:\n{}'.format(docs_url)
    )

    # Optional arguments
    ap.add_argument(
        '-l',
        '--logging-config-file',
        help='configuration file with the logging options',
        default=None,
        dest='logging_config_file',
        type=str,
    )
    ap.add_argument(
        '-s',
        '--server-config-file',
        help='configuration file with the Alarm Manager options',
        default=None,
        dest='server_config_file',
        type=str,
    )
    ap.add_argument(
        '-d',
        '--device-config-file',
        help='configuration file with the device options',
        default=None,
        dest='device_config_file',
        type=str,
    )
    ap.add_argument(
        '-db',
        '--database-config-file',
        help='configuration file with the Database options',
        default=None,
        dest='database_config_file',
        type=str,
    )
    ap.add_argument(
        '-a',
        '--address',
        help='host address',
        default=None,
        dest='host',
        type=str
    )
    ap.add_argument(
        '-p',
        '--port',
        help='host port',
        default=None,
        dest='port',
        type=int
    )

    # Mutually exclusive positional arguments
    pos_arg = ap.add_mutually_exclusive_group()
    pos_arg.add_argument(
        '--run',
        action='store_true',
        help='starts the Lakeshore336 Daemon',
        default=False,
    )
    pos_arg.add_argument(
        '--control',
        type=str,
        help='send a control command to the running Lakeshore336 Daemon',
        nargs='?',
    )

    # Auto-start option for supervisord
    ap.add_argument(
        '--autostart',
        action='store_true',
        help='start the Lakeshore336 Daemon, connect to the device and start monitoring',
        default=False,
        dest='autostart',
    )

    # Parse the arguments
    args, extra = ap.parse_known_args(args=argv[1:])
    if extra is not None and args.control is not None:
        args.control += ' ' + ' '.join(extra)

    # Call appropriate function
    if args.run:
        run(args)
    else:
        send_message(args)


def send_message(args: Namespace):
    """ Sends a string message to a running Lakeshore
    336 :class:`Daemon` object over TCP."""

    try:
        # Start a client
        c = Client(
            config_file=args.server_config_file,
            host=args.host,
            port=args.port,
        )
        print('Opening connection to the Lakeshore 336 server on {h}:{p}'.format(
            h=c.host,
            p=c.port
        ))

        # Send message and get reply
        print('Sending message: ', args.control)
        reply = c.send_message(args.control)
        print('Reply:\n', reply)

    except ConfigError:
        print('Did you provide a valid configuration file?')

    except OSError:
        print('Maybe the Lakeshore 336 server is not running, or running elsewhere')

    except BaseException as e:
        # Undefined exception, full traceback to be printed
        print("{}: {}".format(type(e).__name__, e))

    else:
        exit(0)

    # Something went wrong...
    exit(1)


def run(args: Namespace):
    """ Launches a Lakeshore 336
    :class:`Daemon` object."""

    try:
        # Setup logging
        configure_logging(
            config_file=args.logging_config_file,
            logger_name='Lakeshore336'
        )

        # Start the daemon
        getLogger().info('Starting the Lakeshore 336 server...')
        the_daemon = Daemon(
            config_file=args.server_config_file,
            pid_file_name='/tmp/lakeshore336.pid',
            host=args.host,
            port=args.port,
            autostart=args.autostart,
            device_config_file=args.device_config_file,
            database_config_file=args.database_config_file,
        )

        the_daemon.start_daemon()
        getLogger().info('Lakeshore 336 server stopped, bye!')

    except ConfigError as e:
        getLogger().error("{}: {}".format(type(e).__name__, e))
        getLogger().error('Did you provide a valid configuration file?')

    except OSError as e:
        getLogger().error("{}: {}".format(type(e).__name__, e))
        getLogger().error('Possible socket error, do you have permissions to the socket?')

    except LockError as e:
        getLogger().error("{}: {}".format(type(e).__name__, e))
        getLogger().error('Lakeshore336 daemon is probably running elsewhere.')

    except BaseException as e:
        # Undefined exception, full traceback to be printed
        getLogger().exception("{}: {}".format(type(e).__name__, e))

    else:
        exit(0)

    # Something went wrong...
    exit(1)
