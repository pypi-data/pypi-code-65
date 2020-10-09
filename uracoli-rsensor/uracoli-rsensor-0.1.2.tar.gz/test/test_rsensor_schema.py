import unittest, os, shutil
import sqlite3, pymysql


SCHEMA = "rsensor_schema.sql"

@unittest.skip("out of order for now")
class TestSQlite(unittest.TestCase):

    dbname = "tst_rsensor.db"
    dbcon = None
    dbcur = None


    def query(self, stmt):
        rv = self.dbcur.execute(stmt)
        return rv.fetchall()

    def setUp(self):
        # create empty sqlite3 db

        try:
            os.remove(self.dbname)
        except OSError:
            pass
        self.dbcon = sqlite3.connect(self.dbname)
        self.dbcur = self.dbcon.cursor()
        self.dbcur.execute("PRAGMA foreign_keys = ON;")
        with open(SCHEMA,"r") as f:
            self.dbcon.executescript(f.read())
            f.close()

    def test_inv_insert(self):
        self.assertRaises(sqlite3.IntegrityError, self.query,
                          "INSERT INTO sensor (sens_name, meas_id) VALUES ('foo2', 43)" )

    def test_val_insert(self):
        x = self.query("INSERT INTO meas_series (meas_id, sens_name, tbl_name) VALUES (42, 'foo1', 't_foo1')")
        x = self.query("INSERT INTO sensor (sens_name, meas_id) VALUES ('foo1', 42)")

@unittest.skip("out of order for now")
class TestMySQL(unittest.TestCase):
    dbname = "tst_rsensor"

    def query(self, stmt):
        rv = self.dbcur.execute(stmt)
        return rv

    @classmethod
    def setUpClass(cls):
        dbcon = pymysql.connect(user = "root")
        dbcur = dbcon.cursor()
        dbcur.execute("DROP DATABASE IF EXISTS %s;" % cls.dbname)
        dbcur.execute("CREATE DATABASE %s;" % cls.dbname)
        print "setUpClass done"

    def setUp(self):
        self.dbcon = pymysql.connect(user = "root", db = self.dbname )
        self.dbcur = self.dbcon.cursor()
        with open(SCHEMA,"r") as f:
            self.dbcur.execute(f.read())
            f.close()
        self.dbcur.execute("FLUSH;")
        dbcon.commit()


    def tearDown(self):
        # save changes for eventual debugging
        self.dbcon.commit()

    def test_val_insert(self):
        x = self.query("INSERT INTO meas_series (meas_id, sens_name, tbl_name) VALUES (42, 'foo1', 't_foo1');")
        x = self.query("INSERT INTO sensor (sens_name, meas_id) VALUES ('foo1', 42);")

    def test_inv_insert(self):
        self.assertRaises(pymysql.err.IntegrityError, self.query,
                          "INSERT INTO sensor (sens_name, meas_id) VALUES ('foo2', 43)" )

if __name__ == '__main__':
    unittest.main()