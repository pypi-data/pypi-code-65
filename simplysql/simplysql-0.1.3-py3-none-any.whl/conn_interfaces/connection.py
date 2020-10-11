#! /usr/bin/python3.7.6
import sqlite3


class Connection():
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._cursor = None
        self._connection = None

        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    @property
    def connection(self):
        return self._connection

    @property
    def cursor(self):
        return self._cursor

    @property
    def description(self):
        if self.cursor:
            return self.cursor.description
        return None

    def connect(self):
        self._connection = sqlite3.connect(self._db_path)
        self._cursor = self._connection.cursor()
        self.open = True

    def commit(self):
        self.connection.commit()

    def close(self, commit: bool = True):
        if commit:
            self.commit()

        self.cursor.close()
        self.connection.close()
        self.open = False

    def execute(self, sql: str, params=None):
        self.cursor.execute(sql, params or ())
        self.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql: str, params=None):
        self.execute(sql, params or ())
        return self.fetchall()

    def __repr__(self) -> str:
        return "Connection {}".format("is open" if self.open else "is closed")
