import sqlite3
import logging


class SQLiteHandler:

    def __init__(self, name: str = None):
        self.name = name
        self.conn = None
        self.cursor = None
        self._connected = False
        self.query = ''
        if name:
            self.connect()

    def backup(self, name: str = None):
        logging.info('Creating backup of {}'.format(self.name))
        backup_name = name if name is not None else '{} - Backup.db'.format(self.name)
        backup = sqlite3.connect(backup_name)
        with backup:
            self.conn.backup(backup)
        backup.close()
        logging.info('Backup of {} created: {}'.format(self.name, backup))

    def connect(self, name: str = None):
        """Connects to the database"""
        if name is not None:
            self.name = name
        try:
            self.conn = sqlite3.connect(self.name)
            self.conn.execute('PRAGMA foreign_keys = 1')
            self.cursor = self.conn.cursor()
            self._connected = True
            logging.info('Connected to database: {}'.format(self.name))
        except sqlite3.Error as err:
            logging.error('Error connecting to database "{}": {}'.format(self.name, err))

    def close(self):
        """Commit and close database"""
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            self._connected = False
        logging.info('Closed database: {}'.format(self.name))

    def commit(self):
        """Commit to database"""
        logging.info('Committing to database.')
        self.conn.commit()

    def execute(self, query: str = None, param=None):
        if query is None:
            query = self.query
            self.query = ''
        logging.info('Executing query: {}'.format(query))
        # Todo: Might add params to logging later
        try:
            if param is not None:
                return self.conn.execute(query, param)
            else:
                return self.conn.execute(query)
        except sqlite3.IntegrityError as err:
            logging.error(err)

    def executescript(self, query: str):
        logging.info('Executing query: {}'.format(query))
        return self.conn.executescript(query)

    def __bool__(self):
        return self._connected

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
