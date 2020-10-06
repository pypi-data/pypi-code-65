from pathlib import Path
from unittest import TestCase

from psycopg2 import connect
from psycopg2._psycopg import connection as Connection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from testing.postgresql import Postgresql


class DatabaseTestCase(TestCase):
    _postgres: Postgresql
    _conn: Connection

    @classmethod
    def setUpClass(cls) -> None:
        cls._postgres = Postgresql()
        cls._conn = connect(cls._postgres.url())

        cls._conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        fixtures_path = Path(__file__).resolve().parent / "fixtures"
        with open(Path(fixtures_path) / "schema.sql") as f:
            sql = f.read()

        with cls._conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._postgres.stop()
