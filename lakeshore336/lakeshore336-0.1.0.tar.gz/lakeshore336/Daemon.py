""" Daemon TCP server. The server will run indefinitely
listening on the specified TCP (see the
:class:`~lab_utils.socket_comm.Server` documentation).
When a client connects and sends a message string, the
message parser will call the appropriate method. The
following commands are supported by the parser (options
must be used with a double dash \\- \\-):

+-----------+-----------------------+---------------------------------------------------------------------------+
| quit      |                       | Stops the daemon and cleans up database and serial port                   |
+-----------+-----------------------+---------------------------------------------------------------------------+
| status    |                       | TODO: Not implemented yet                                                 |
+-----------+-----------------------+---------------------------------------------------------------------------+
| lakeshore | on/off/restart        | Connects / disconnects / restarts the TPG 256A device                     |
+           +-----------------------+---------------------------------------------------------------------------+
|           | test                  | Performs a connection test and returns the device firmware                |
+           +-----------------------+---------------------------------------------------------------------------+
|           | config {file}         | Reloads the default (or given) config file (logging is stopped)           |
+           +-----------------------+---------------------------------------------------------------------------+
|           | single-readout        | Performs a single read-out to the device (logging is stopped)             |
+-----------+-----------------------+---------------------------------------------------------------------------+
| logging   | start / stop          | Launches or stops the separate device monitoring thread                   |
+           +-----------------------+---------------------------------------------------------------------------+
|           | terminal              | Prints output to the terminal with *info* level                           |
+           +-----------------------+---------------------------------------------------------------------------+
|           | use-database          | Enables data saving to a PostgreSQL database                              |
+-----------+-----------------------+---------------------------------------------------------------------------+

"""

# Imports
import argparse
from psycopg2 import DatabaseError
from configparser import Error as ConfigError

# Third party
from lab_utils.socket_comm import Server

# Local
from .Lakeshore336 import LakeShore336, UserCurve
from lakeshore import InstrumentException
from .Monitor import Monitor
from .__project__ import (
    __documentation__ as docs_url,
    __description__ as prog_desc,
    __module_name__ as mod_name,
)


def nice_header(header: str) -> str:
    if len(header) < 1:
        return header
    reply = ''.join('-' for _ in range(len(header)))
    reply += '\n'
    reply += header
    reply += ''.join('-' for _ in range(len(header)))
    reply += '\n'
    return reply


def nice_trailer(header: str) -> str:
    if len(header) < 1:
        return ''
    reply = ''.join('-' for _ in range(len(header)))
    reply += '\n\n'
    return reply


class Daemon(Server):
    """ Base class of the daemon, derived from
    :class:`~lab_utils.socket_comm.Server`. The daemon
    holds pointers to the :attr:`device` driver and the
    :attr:`monitor` thread, and communicates with them
    upon message reception. """

    # Attributes
    device: LakeShore336 = None     #: Device handler.
    monitor: Monitor = None         #: Monitor thread.

    use_db: bool = False
    db_file: str = None
    use_terminal: bool = False

    def __init__(self,
                 config_file: str = None,
                 pid_file_name: str = None,
                 host: str = None,
                 port: int = None,
                 autostart: bool = False,
                 device_config_file: str = None,
                 database_config_file: str = None,
                 ):
        """ Initializes the :class:`Daemon` object.
        The :attr:`device` constructor is called:
        serial connection is established and hardware
        information is retrieved from the controller.

        Parameters
        ----------
        config_file : str, optional
            See parent class :class:`~lab_utils.socket_comm.Server`.

        pid_file_name : str, optional
            See parent class :class:`~lab_utils.socket_comm.Server`.

        host : int, optional
            See parent class :class:`~lab_utils.socket_comm.Server`.

        port : int, optional
            See parent class :class:`~lab_utils.socket_comm.Server`.

        autostart : bool, optional
            Connect to the device and start monitoring.

        device_config_file : str, optional
            Configuration file for the TPG-256A :attr:`device`.

        database_config_file : str, optional
            Configuration file for the database. If given and
            :paramref:`~Daemon.__init__.autostart` is 'True',
            a :class:`Monitor` thread will be launched with
            database option active.

        Raises
        ------
        :class:`configparser.Error`
            Configuration file error

        :class:`LockError`
            The PID file could not be locked (see parent
            class :class:`~lab_utils.socket_comm.Server`).

        :class:`OSError`
            Socket errors (see parent class
            :class:`~lab_utils.socket_comm.Server`).

        :class:`~serial.SerialException`
            The connection to the :attr:`device` has failed

        :class:`IOError`
            Communication error, probably message misspelt.

        :class:`StateError`
            :attr:`device` was in the wrong state, e.g. already ON.

        """
        # Call the parent class initializer
        super().__init__(
            config_file=config_file,
            pid_file_name=pid_file_name,
            host=host,
            port=port,
        )

        if database_config_file is not None:
            self.use_db = True
            self.db_file = database_config_file

        # Add custom arguments to the message parser
        self.update_parser()

        # Initialize and connect to the device
        self.device = LakeShore336(config_file=device_config_file)

        # Autostart?
        if not autostart:
            return
        else:
            self.logger.info('Launching auto-start sequence')

        # Start background monitor thread
        self.monitor = Monitor(
            device=self.device,
            name='Daemon Thread',
            terminal_flag=False,    # the autostart option is meant to be used with supervisord, no terminal output
            database_flag=database_config_file is not None,
            database_config_file=database_config_file,
        )
        self.logger.info('Monitor thread launched!')

    def update_parser(self):
        """ Sets up the message
        :attr:`~lab_utils.socket_comm.Server.parser`. """

        self.logger.debug('Setting up custom message parser')

        # Set some properties of the base class argument parser
        self.parser.prog = mod_name
        self.parser.description = prog_desc
        self.parser.epilog = 'Check out the package documentation for more information:\n{}'.format(docs_url)

        # Subparsers for each acceptable command
        # 1. STATUS
        sp_status = self.sp.add_parser(
            name='status',
            description='checks the status of the daemon',
        )
        sp_status.set_defaults(
            func=self.status,
            which='status')

        # 2. TPG-256A
        sp_lakeshore = self.sp.add_parser(
            name='lakeshore',
            description='interface to the Lakeshore 336 device',
        )
        sp_lakeshore.set_defaults(
            func=self.lakeshore,
            which='lakeshore'
        )
        sp_lakeshore.add_argument(
            '--restart, -r',
            action='store_true',
            help='restarts the connection',
            default=False,
            dest='restart',
        )
        sp_lakeshore.add_argument(
            '--config,-c',
            default=argparse.SUPPRESS,      # If --config is not given,  it will not show up in the namespace
            nargs='?',                      # If --config is given, it may be used with or without an extra argument
            const=None,                     # If --config is given without an extra argument, 'dest' = None
            help='reloads the configuration file (and resets the file if given, absolute path only)',
            dest='config_file',
        )
        sp_lakeshore.add_argument(
            '--device-info,-s',
            action='store_true',
            help='prints device information',
            default=False,
            dest='device_info',
        )
        sp_lakeshore.add_argument(
            '--single-readout,-r',
            action='store_true',
            help='performs a single readout to the device',
            default=False,
            dest='single_readout',
        )

        # 3. Monitor
        sp_monitor = self.sp.add_parser(
            name='logging',
            description='manages the logging thread',
        )
        sp_monitor.set_defaults(
            func=self.logging,
            which='logging'
        )
        sp_g2 = sp_monitor.add_mutually_exclusive_group()
        sp_g2.add_argument(
            '--start',
            action='store_true',
            help='starts the monitor thread',
            default=False,
            dest='start',
        )
        sp_g2.add_argument(
            '--stop',
            action='store_true',
            help='stops the monitor thread',
            default=False,
            dest='stop',
        )
        sp_monitor.add_argument(
            '--terminal',
            action='store_true',
            help='prints the monitor output to the application logging sink',
            default=False,
            dest='terminal',
        )
        sp_monitor.add_argument(
            '--use-database',
            default=argparse.SUPPRESS,  # If --use-database is not given it will not show up in the namespace
            nargs='?',                  # If --use-database is given it may be used with or without an extra argument
            const=None,                 # If --use-database is given without an extra argument, 'dest' = None
            help='logs data to a PostgreSQL database using the given config file, or the default one',
            dest='database_config_file',
        )

        # 4. Retrieve user curve
        sp_curve_retrieve = self.sp.add_parser(
            name='curve_retrieve',
            description='retrieves a user curve',
        )
        sp_curve_retrieve.set_defaults(
            func=self.curve_retrieve,
            which='curve_retrieve'
        )
        sp_curve_retrieve.add_argument(
            '--curve-id,-c',
            default=21,
            type=int,
            help='curve ID to retrieve',
            dest='curve_id'
        )
        sp_curve_retrieve.add_argument(
            '--save-file,-f',
            help='save retrieved curve to file',
            default=None,
            dest='curve_save_file',
            type=str
        )

        # 5. Load user curve
        sp_curve_load = self.sp.add_parser(
            name='curve_load',
            description='loads a user curve',
        )
        sp_curve_load.set_defaults(
            func=self.curve_load,
            which='curve_load'
        )
        sp_curve_load.add_argument(
            'filename',
            type=str,
            help='file with curve data to load'
        )

    def quit(self):
        """ Stops the daemon, called with message 'quit'.
        The method overrides the original
        :meth:`~lab_utils.socket_comm.Server.quit` to do
        proper clean-up of the monitoring
        :attr:`thread<monitor>` and the :attr:`device`
        handler.
        """

        self.logger.info('Launching quitting sequence')

        try:
            # Monitor
            self._stop_logging(quiet=True)

            # Device
            self.device.unlock()
            self.device.disconnect_tcp()

        except RuntimeError as e:
            self.reply += 'Monitor thread error! {}: {}'.format(type(e).__name__, e)

        except (InstrumentException, IOError) as e:
            self.reply += 'Device error! {}: {}'.format(type(e).__name__, e)
        else:
            self.reply += 'Device is now disconnected, terminating TCP daemon'

    def status(self):
        """ TODO
        """
        self.reply += 'Status: doing great!'

    def lakeshore(self):
        """ Modifies or checks the status of the Lakeshore 336
        :attr:`device`. Provides functionality to:

        -  Configure the controller.
        -  Retrieve hardware information.
        -  Reload device configuration.
        -  Perform a single read-out of the sensors
        """
        self.logger.debug('Method \'lakeshore\' called by the message parser')

        # Restart device
        if self.namespace.restart:
            try:
                self._restart_device()
            except BaseException as e:
                self.reply += 'Error! {}: {}'.format(type(e).__name__, e)
                return
            self.reply += 'Device was restarted\n'

        # Reset and load configuration file
        if "config_file" in self.namespace:
            try:
                self._reload_config()
            except BaseException as e:
                self.reply += 'Error! {}: {}'.format(type(e).__name__, e)
                return

            self.reply += 'Device was reconfigured\n'
            if self.namespace.config_file is not None:
                self.reply += 'New configuration file: {}\n'.format(self.device.config_file)

        # Device information
        if self.namespace.device_info:
            # Print device information
            self.reply += self._device_info()

        self.reply += 'Lakeshore routine completed\n'

    def _restart_device(self):
        """ Restarts the device. If the device was initially
        logging, it is also stopped and relaunched afterwards.

        Raises
        ------
        :class:'lakeshore.InstrumentException`
            Lakeshore 336 device error

        :class:`configparser.Error`
            Database configuration file error.

        :class:`psycopg2.DatabaseError`
            Database error (connection, access...)

        :class:'RuntimeError`
            The monitor thread could not be stopped within 5 seconds.
        """

        self.logger.info('Initializing restart sequence')

        # Stop logging, reconnect, and start logging if necessary
        logging_active = self._is_logging()
        if logging_active:
            self._stop_logging(quiet=True)

        self.device.reconnect()

        if logging_active:
            self._start_logging()

    def _reload_config(self):
        """ Reloads the device configuration. If the device
        was initially logging, it is also stopped and
        relaunched afterwards.

        Raises
        ------
        :class:'lakeshore.InstrumentException`
            Lakeshore 336 device error

        :class:`configparser.Error`
            Database configuration file error.

        :class:`psycopg2.DatabaseError`
            Database error (connection, access...)

        :class:'RuntimeError`
            The monitor thread could not be stopped within 5 seconds.
        """

        self.logger.info('Reloading device configuration')

        # Stop logging, reconnect, and start logging if necessary
        logging_active = self._is_logging()
        if logging_active:
            # Save current configuration of the logging thread
            self.namespace.terminal = self.monitor.terminal_flag
            if self.monitor.database_flag:
                self.namespace.database_config_file = self.monitor.database_config_file

            # Stop the thread
            self._stop_logging(quiet=True)

        # Reconfigure device
        self.device.config(new_config_file=self.namespace.config_file)
        self.device.apply_config()

        # Start logging if necessary
        if logging_active:
            self._start_logging()

    def _device_info(self) -> str:
        """ Summarizes the device configuration and status.

        Returns
        -------
        str
            The nicely formatted summary.
        """

        # Input sensors
        header = '{:15}{:15}{}\n'.format('Sensor', 'Logging', 'Latest Value')
        reply = nice_header(header)

        for ch in self.device.channel_info:
            if ch.label is None:
                continue
            status = 'Yes'
            if not ch.logging:
                status = 'No'
            data_res = 'None'
            if ch.data_res is not None:
                data_res = ch.data_res
            data_temp = 'None'
            if ch.data_temp is not None:
                data_temp = ch.data_temp
            reply += '{:<15}{:<15}{:<15}{:<15}\n'.format(ch.label, status, str(data_res), str(data_temp))
        reply += nice_trailer(header)

        # Output heaters
        header = '{:<15}{:<15}{:<20}{:<20}{:<20}{}\n'.format(
            'Heater',
            'Active',
            'Control Input',
            'Resistance [Ohm]',
            'Max Current [A]',
            'Latest Power'
        )
        reply += nice_header(header)

        for h in self.device.heater_info:
            if h.active:
                data = 'None'
                if h.data is not None:
                    data = '{} %'.format(h.data * 100)

                reply += '{:<15}{:<15}{:<20}{:<20}{:<20}{:<15}\n'.format(
                    h.heater_id,
                    'Yes',
                    'Sensor {}'.format(h.control_input),
                    h.resistance,
                    h.max_current,
                    data,
                )
            else:
                reply += '{:<15}{:<15}{:<20}{:<20}{:<20}{:<15}\n'.format(
                    h.heater_id,
                    'No',
                    '-',
                    '-',
                    '-',
                    '-',
                )
        reply += nice_trailer(header)
        return reply

    def logging(self):
        """ Manages the :attr:`logging thread<monitor>`.
        Provides functionality to start and stop the thread.
        """
        self.logger.debug('Method \'logging\' called by the message parser')

        # Use database
        self.use_db = "database_config_file" in self.namespace
        if self.use_db:
            self.db_file = self.namespace.database_config_file

        # Use terminal
        self.use_terminal = self.namespace.terminal

        # Start
        if self.namespace.start:
            try:
                self._start_logging()
                self.reply += 'Daemon Thread launched\nYou can check its status with the \'status\' option\n'
            except (InstrumentException, RuntimeError, DatabaseError, ConfigError) as e:
                self.reply += 'Error launching Daemon Thread! {}: {}'.format(type(e).__name__, e)
                return

        # Stop
        if self.namespace.stop:
            try:
                self._stop_logging()
                self.use_db = False
                self.db_file = ''
                self.use_terminal = False
                self.reply += 'Daemon thread stopped\n'
            except RuntimeError as e:
                self.reply += 'Error stopping Daemon Thread! {}: {}'.format(type(e).__name__, e)
                return

    def _is_logging(self) -> bool:
        """ Checks whether the :attr:`logging thread<monitor>` is running.

        Returns
        -------
        bool
            True if the monitor is running, False otherwise.

        """
        return self.monitor is not None and self.monitor.is_alive()

    def _start_logging(self):
        """ Creates and starts the :attr:`logging thread<monitor>`.

        Raises
        ------
        :class:'lakeshore.InstrumentException`
            Lakeshore 336 device error

        :class:`configparser.Error`
            Database configuration file error.

        :class:`psycopg2.DatabaseError`
            Database error (connection, access...)

        """
        # Check the monitor is not running yet
        if self._is_logging():
            self.logger.warning('Monitor thread is already running')
            self.reply += 'Monitor thread is already running\n'
            return

        # Launch monitor thread
        self.logger.info('Launching logging thread')
        self.monitor = Monitor(
            device=self.device,
            name='Daemon Thread',
            terminal_flag=self.use_terminal,
            database_flag=self.use_db,
            database_config_file=self.db_file,
        )

    def _stop_logging(self, quiet: bool = False):
        """ Signals a running :attr:`logging thread<monitor>` to stop.

        Parameters
        ----------
        quiet : bool, optional
            If True, no output is produced for the initial running check

        Raises
        -------
        :class:'RuntimeError`
            The monitor thread could not be stopped within 5 seconds.
        """

        # Check monitor is actually running
        if not self._is_logging():
            if not quiet:
                self.logger.info('Monitor thread is not running')
                self.reply += 'Monitor thread is not running\n'
            return

        # Signal the monitor to stop
        self.logger.info('Stopping logging thread')
        self.monitor.stop()

    def curve_retrieve(self):
        self.logger.debug('Method \'curve_retrieve\' called by the message parser')

        # Namespace parsing
        filename = self.namespace.curve_save_file

        # Retrieve curve
        curve = self.device.curve_retrieve(
            self.namespace.curve_id,
            only_header=filename is None
        )

        # Parse reply
        self.reply += nice_header('Curve {} - {}\n'.format(curve.id, curve.name))
        self.reply += '{:20} {}\n'.format('Serial Number:', curve.serial_number)
        self.reply += '{:20} {}\n'.format('Format:',        curve.format.name)
        self.reply += '{:20} {}\n'.format('Limit Value:',   '{} K'.format(curve.limit_value))
        self.reply += '{:20} {}\n'.format('Coefficient:',   curve.coefficient.name)

        # Save to file
        if filename is not None:
            curve.write_to_file(filename)
            self.reply += '{:20} {}\n'.format('Data file:',   filename)

    def curve_load(self):
        self.logger.debug('Method \'curve_load\' called by the message parser')

        # Read curve from file
        curve = UserCurve()
        try:
            curve.read_from_file(self.namespace.filename)
        except:
            pass

        # Parse reply
        self.reply += nice_header('Curve {} - {}\n'.format(curve.id, curve.name))
        self.reply += '{:20} {}\n'.format('Serial Number:', curve.serial_number)
        self.reply += '{:20} {}\n'.format('Format:',        curve.format.name)
        self.reply += '{:20} {}\n'.format('Limit Value:',   '{} K'.format(curve.limit_value))
        self.reply += '{:20} {}\n'.format('Coefficient:',   curve.coefficient.name)

        # Load curve
        self.device.curve_load(curve)
