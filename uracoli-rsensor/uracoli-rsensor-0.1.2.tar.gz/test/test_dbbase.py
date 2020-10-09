import unittest
import rsensor.database.dbbase as db
import sys


class DbMock(db.DbBase):
    # === interface functions =================================================
    def execute_script(self, fn):
        print Exception("NotImplemented")


    def get_tables(self):
        print Exception("NotImplemented")

    def query(self, stmt):
        print Exception("NotImplemented")

    def xquery(self, stmt):
        print Exception("NotImplemented")

    def commit(self):
        print Exception("NotImplemented")    

# === test case class
class TestDbBase(unittest.TestCase):
    
    def test_init_ok(self):
        db = DbMock("rsensor/database/schema.yml")
        
        print db
    
    def test_init_fail(self):
        with self.assertRaises(IOError):
            DbMock("none_existing_schema.yml")
    
    def test_foo(self):
        assert 1 == 1

if __name__ == "__main__":
    unittest.main()