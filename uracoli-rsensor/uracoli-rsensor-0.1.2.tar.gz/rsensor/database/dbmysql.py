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


# === imports ================================================================
from __future__ import print_function
from dbbase import DbBase
import logging
import pymysql

# === classes ==================================================================
class DbMySQL(DbBase):

    # constructor
    def __init__(self, dbname, dbschema, dbhost, dbuser, dbpasswd, **kwargs):
        self.L = logging.getLogger("DbMysql")
        self.dbcon = None
        self.L.info("schema: %s, args: %s", dbschema, kwargs)
        self.dbcon = pymysql.connect(host = dbhost, user = dbuser, password = dbpasswd, db = dbname)
        self.dbcur = self.dbcon.cursor(pymysql.cursors.DictCursor)
        DbBase.__init__(self, dbschema, False)

    # destructor
    def __del__(self):
        if self.dbcon:
            self.dbcon.close()
            print("destroyed", self.dbcon)

    def execute_script(self, fn):
        self.L.info("fn: %s", fn)
        with open(fn, "r") as f:
            self.dbcur.execute(f.read())
        self.dbcon.commit()

    def query(self, stmt):
        self.L.debug("MySql-Query: %s", stmt)
        x = self.dbcur.execute(stmt)
        if x:
            rv = list(self.dbcur)
        else:
            rv = []
        return rv

    # writes last changes into DB (e.g. update, insert, replace, ... )
    def commit(self):
        self.dbcon.commit()

