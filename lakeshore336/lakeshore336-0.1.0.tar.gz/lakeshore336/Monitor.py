""" Background monitoring thread based on the :obj:`threading`
library. A :obj:`Monitor` object starts a background
:class:`thread<threading.Thread>` which reads out the Lakeshore 336
:attr:`~Monitor.device` every second. The data can then be
printed to the terminal and/or saved to a PostgreSQL database
using the :obj:`lab_utils.database` library. The monitoring
thread is intended to be self-sustainable and will try to deal
with unexpected errors (usually issues with communication to
the device), recover, log them and keep running.
"""

# Imports
from datetime import datetime
from time import sleep
from threading import Thread, Event
from typing import List

# Third party
from lab_utils.database import Database, DataType, Constraint
from lab_utils.custom_logging import getLogger

# Local
from .Lakeshore336 import LakeShore336
from lakeshore import InstrumentException


class Monitor(Thread):
    """ Manages a background
    :class:`thread<threading.Thread>`
    which queries and controls the Lakeshore
    336 :attr:`~Monitor.device`."""

    # Thread objects
    device: LakeShore336 = None     #: :class:`Lakeshore 336<.Lakeshore336>` handler.
    db: Database = None             #: :class:`Database<lab_utils.database.Database>` object.

    # Thread flags
    run_flag: Event = None          #: :class:`Flag<threading.Event>` to signal the thread to stop.
    database_flag: Event = False    #: Database usage :class:`flag<threading.Event>`.
    terminal_flag: Event = False    #: Terminal output :class:`flag<threading.Event>`.

    # Monitor Variables
    database_config_file: str = None    #: Database configuration file
    table_name: str = 'cryosystem'      #: Name of the PostgreSQL table where data will be saved.
    column_list: List[str] = None       #: :class:`~typing.List` of data labels to save.

    def __init__(self,
                 device: LakeShore336,
                 name: str = 'Monitor Thread',
                 database_flag: bool = False,
                 database_config_file: str = None,
                 terminal_flag: bool = False,
                 table_name: str = 'cryosystem'):
        """ Initializes the :class:`Monitor` object. The
        constructor checks that the given :paramref:`device`
        is initialized. If :paramref:`database_flag` is set
        to `True`, the :meth:`prepare_database` method is
        called, which initializes the :attr:`database<db>`
        object and sets up the connection. A table named
        :paramref:`table_name` is created, as well as the
        necessary :attr:`columns<column_list>` to store the
        temperature data.

        Finally, the method :meth:`run` starts and detaches
        a background thread which will run indefinitely,
        reading the Lakeshore 336 :attr:`device`. The data is
        saved to the :attr:`database` if :paramref:`database_flag`
        is set to `True`, and it is printed to the terminal if
        :paramref:`terminal_flag` is set to `True`.

        Parameters
        ----------
        device: :class:`.Lakeshore336`
            Device handle, must be already initialized.

        name: str, optional
            Thread name for logging purposes, default is 'Monitor Thread'

        database_flag: bool, optional
            Save data to a PostgreSQL database, default is 'False'

        terminal_flag: bool, optional
            Print data to the logging terminal sink with 'info'
            level, default is 'False'

        table_name: str, optional
            Name of the PostgreSQL table where the data is saved, default is 'cryo_temperature'.


        Raises
        ------
        :class:'lakeshore.InstrumentException`
            Lakeshore 336 device error

        :class:`configparser.Error`
            Database configuration file error.

        :class:`psycopg2.DatabaseError`
            Database error (connection, access...)
        """

        # Assign arguments
        self.table_name = table_name

        # Check device is ON and ready
        self.device = device

        # Call the parent class initializer
        super().__init__(name=name)

        # Initialize flags
        self.run_flag = Event()
        self.database_flag = Event()
        self.terminal_flag = Event()

        # Set flags
        self.run_flag.set()
        if database_flag:
            getLogger().info('Database option active')
            self.database_flag.set()
            self.database_config_file = database_config_file
        else:
            getLogger().info('Database option not active')

        if terminal_flag:
            getLogger().info('Terminal option active')
            self.terminal_flag.set()
        else:
            getLogger().info('Terminal option not active')

        # Initialize database
        if database_flag:
            self.prepare_database()

        # Run
        self.start()

    def prepare_database(self):
        """ Ensures the :attr:`database<db>` is ready to accept
        data from the Lakeshore 336 :attr:`device`. Initializes
        the :attr:`database<db>` object and sets up the
        connection. If the table :attr:`table_name` does not
        exist, it is created, as well as the necessary
        :attr:`columns<column_list>` to store the temperature
        data. The labels of the columns are retrieved from
        device's :attr:`~.Lakeshore336.channel_info`.

        Raises
        ------
        :class:`configparser.Error`
            Error reading configuration file.

        :class:`psycopg2.Error`
            Base exception for all kinds of database errors.

        """

        getLogger().info('Setting up database')
        self.db = Database(config_file=self.database_config_file)
        self.db.connect(print_version=True)

        # Check table exists, create otherwise
        if not self.db.check_table(self.table_name):
            self.db.create_timescale_db(self.table_name)
            if not self.db.check_table(self.table_name):
                raise RuntimeError('could not create TimescaleDB object \'%s\'', self.table_name)
        getLogger().debug('Table \'%s\' ready', self.table_name)

        # Create column list and initialize database columns
        self.column_list = []
        for ch in self.device.channel_info:
            if ch.logging:
                self.column_list.append('{}_temp'.format(ch.label))
                self.column_list.append('{}_res'.format(ch.label))

        for h in self.device.heater_info:
            if h.active:
                self.column_list.append('heater{}_power'.format(h.heater_id))
                self.column_list.append('heater{}_setp'.format(h.heater_id))

        # Check columns exist, create otherwise
        getLogger().debug('Creating columns: %s', '; '.join(self.column_list))

        for label in self.column_list:
            # Raises an error if the column could not be created
            self.db.new_column(
                table_name=self.table_name,
                column_name=label,
                data_type=DataType.float,
                constraints=[Constraint.positive],
            )
            getLogger().debug('Column \'%s\' ready', label)

        # Recreate aggregate view
        self.db.create_aggregate_view(table_name=self.table_name)

    def stop(self):
        """ Clears the :attr:`run_flag` to signal the
        background thread to stop. The thread status is
        then checked every 0.1 second (up to 5 seconds).
        Returns `True` if the thread stopped, `False`
        otherwise.

        Raises
        -------
        :class:'RuntimeError`
            The monitor thread could not be stopped within 5 seconds.
        """

        getLogger().info('Sending stop signal to the logging thread')
        self.run_flag.clear()

        # Check thread status every 0.1 seconds, for 5 seconds
        for _ in range(50):
            if not self.is_alive():
                getLogger().info('Monitor thread successfully stopped')
                return
            sleep(0.1)

        # Thread should have stopped by now, something went wrong
        getLogger().error('Monitor thread did not finish within a reasonable time.')
        raise RuntimeError('Monitor thread did not finish within a reasonable time.')

    def run(self) -> None:
        """ Monitor method started upon object creation.
        The Lakeshore 336 :attr:`device` is read every second
        in an endless loop. The temperature data may be saved
        to a PostgreSQL :attr:`database<db>` and/or printed
        to the terminal, if the respective :attr:`terminal_flag`
        and :attr:`database_flag` flags were set.

        In case of unexpected error, which might happen e.g. with
        the Ethernet communication protocol, the method will
        try to recover, log any information and continue operations.

        To stop logging and break the loop, the :meth:`stop`
        method should be used to set the :attr:`run_flag`
        flag.

        """

        # Let the server reply to the client to produce a cleaner log
        sleep(0.1)
        getLogger().info('Starting monitor')

        # Wait until the next turn of the second
        seconds = datetime.now().second
        while datetime.now().second == seconds:
            sleep(0.001)
        seconds = datetime.now().second

        # Endless loop, use the stop() method to break it
        while self.run_flag.is_set():
            try:
                # Read data from the device
                self.device.retrieve_data()

                # Save data to database
                self.save_to_database()

                # Print to terminal and/or file
                self.print_string()

            except (InstrumentException, IOError) as e:
                getLogger().error("{}: {}".format(type(e).__name__, e))
                for i in range(5):
                    sleep(2)
                    getLogger().error('Attempting to reset the device (%d out of 5)', i)
                    try:
                        self.device.reconnect()
                    except (InstrumentException, IOError) as e:
                        getLogger().error("{}: {}".format(type(e).__name__, e))
                    else:
                        # Leave the reconnection "for" loop and return to the main "while" loop
                        break
                # The reconnection attempts have failed, terminate the thread and notify the alarm manager
                getLogger().error('Terminating Lakeshore 336 Temperature Controller Thread!')
                raise SystemExit(
                    'Could not re-establish connection to the device after 5 attempts, terminating thread now...'
                )

            # Wait until the next turn of the second
            while datetime.now().second == seconds:
                sleep(0.001)
            seconds = datetime.now().second

        # We reach here when 'run_flag' has been cleared by the stop() method
        getLogger().info('Stop signal! Quitting logging thread')

    def print_string(self):
        """ Prints the retrieved data to the terminal. The log
        level will be `INFO` if :attr:`terminal_flag` is set,
        and `DEBUG` otherwise."""

        # Build message string
        msg = ''
        for ch in self.device.channel_info:
            if ch.logging:
                # Channel temperature
                t = 'NaN'
                if ch.data_temp is not None:
                    t = ch.data_temp

                # Channel resistance
                r = 'NaN'
                if ch.data_res is not None:
                    r = ch.data_res

                # Format message
                msg += '{:30}'.format('{:7}: {:>10} Ohm - {:<10}'.format(ch.label, r, '{} K'.format(t)))

        for h in self.device.heater_info:
            if h.active:
                # Heater output
                o = 'Invalid'
                if h.data is not None:
                    o = h.data

                # Heater setpoint
                s = '{} K'.format(h.set_point)

                # Format message
                msg += '{:20}'.format('Heater {}: {:>10} - {:<10}'.format(h.heater_id, o, s))

        # Print to terminal
        if self.terminal_flag.is_set():
            getLogger().info(msg)
        else:
            getLogger().debug(msg)

    def save_to_database(self):
        """ Saves the latest system data to the
        PostgreSQL :attr:`database<db>`. If
        :attr:`database_flag` is not set, the
        method does nothing.

        Raises
        ------
        :class:`psycopg2.Error`
            Base exception for all kinds of database errors.
        """

        # Check database flag
        if not self.database_flag.is_set():
            return

        # Build data
        data = []
        for ch in self.device.channel_info:
            if ch.logging:
                # Channel temperature
                if ch.data_temp is None:
                    data.append('NaN')
                    data.append('NaN')
                else:
                    data.append(ch.data_temp)

                # Channel resistance
                if ch.data_res is None:
                    data.append('NaN')
                    data.append('NaN')
                else:
                    data.append(ch.data_res)

        for h in self.device.heater_info:
            if h.active:
                # Heater output
                if h.power is None:
                    data.append('NaN')
                else:
                    data.append(h.power)

                # Heater setpoint
                data.append(h.set_point)

        self.db.new_entry(
            table_name=self.table_name,
            columns=self.column_list,
            data=data,
            check_columns=False,
        )
