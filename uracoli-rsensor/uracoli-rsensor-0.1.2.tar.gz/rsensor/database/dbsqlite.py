#   Copyright (c) 2014 - 2020 Axel Wachtler
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the authors nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#   POSSIBILITY OF SUCH DAMAGE.

# === imports ==================================================================
from __future__ import print_function
import logging
import os
import sqlite3

from dbbase import DbBase


# === functions ================================================================
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# === classes ==================================================================
class DbSqlite(DbBase):
    """Sqlite Interface
    """
    # constructor
    def __init__(self, dbschema, forcetables = False, **kwargs):
        self.L = logging.getLogger("DbSqlite")
        self.dbcon = None
        self.L.info("use schema: %s", dbschema)
        #: database connection instance
        dbfile = os.path.abspath(os.path.normpath(kwargs["dbname"]))
        dirname, _ = os.path.split(dbfile)
        if not os.path.isdir(dirname):
            self.L.info("create directory: %s", dirname)
            os.makedirs(dirname)
        self.L.info("open sqlite file: %s", dbfile)
        

        self.dbcon = sqlite3.connect(dbfile)
        self.dbcon.row_factory = dict_factory
        #: database cursor instance
        self.cur = self.dbcon.cursor()
        DbBase.__init__(self, dbschema, forcetables)
        
    # destructor
    def __del__(self):
        if self.dbcon:
            self.dbcon.close()
            self.L.info("destroyed: %s", self.dbcon)

    def execute_script(self, fn):
        """ececute SQL script file

        :param str fn: name of the script
        """
        with open(fn, "r") as f:
            self.L.debug("fn: %s", fn)
            txt = f.read()
            self.L.debug("txt: %s", txt)
            self.dbcon.executescript(txt)

    def get_tables(self):
        rv = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        return [x['name'] for x in rv]

    # returns list of dictionaries
    def query(self, stmt):
        self.L.debug("query: %s", stmt)
        self.last_stmt = stmt
        self.cur.execute(stmt)
        return self.cur.fetchall()

    # yields the result dictionaries
    def xquery(self, stmt):
        self.last_stmt = stmt
        self.cur.execute(stmt)
        while 1:
            rv = self.cur.fetchone()
            if rv:
                yield rv
            else:
                break

    # writes last changes into DB (e.g. update, insert, replace, ... )
    def commit(self):
        self.dbcon.commit()

if __name__ == "__main__":
    # some testcode
    db = DbSqlite(dbname = "../../test/my_rsensor.db");
    for x in db.xquery("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"):
        print("table:", x)
    print(db.query("select * from s3333_0001_00_temp limit 10"))
    print(db.query("select * from s3333_0001_00_temp where time = 42.4242"))
    print(db.query("select max(value), min(value), avg(value), count(value) from s3333_0001_00_temp"))
    print(db.query("select max(value) as max, min(value) as min, avg(value) as avg, count(value) as cnt from s3333_0001_00_temp"))
