import unittest
import rsensor.database.dbsqlite as dbs
import sys
import os, errno


# === test case class
class TestDbSqlite(unittest.TestCase):

    @staticmethod
    def silentremove(filename):
        try:
            os.remove(filename)
        except OSError as e: # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occurred

    def test_init_ok(self):
        self.silentremove("test/test_ok.sqlite")
        db = dbs.DbSqlite("test/test_ok.sqlite", "rsensor/database/schema.yml")
        assert os.path.exists("test/test_ok.sqlite")
        #print("tables:", db.query(".tables"))
        
    def test_init_fail(self):
        with self.assertRaises(IOError):
            self.silentremove("test/test_fail.sql")
            dbs.DbSqlite("test/test_fail.sql", "none_existing_schema.yml")
