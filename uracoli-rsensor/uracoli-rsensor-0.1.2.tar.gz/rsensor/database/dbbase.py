#   Copyright (c) 2014 - 2017 Axel Wachtler
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
import logging
import yaml

# === classes ==================================================================
class DbBase:
    
    #: data structure that holds the schema of the DB
    DbSchema = None
    
    def __init__(self, dbschema, forcetables, **kwargs):        
        self.L = logging.getLogger("DbBase")        
        self.DbSchema = self.load_yaml_schema(dbschema)
        sql = self.create_tables(force = forcetables)
        for i,x in enumerate(sql):
            self.L.debug("%d: %s", i, x)
            self.query(x)
        self.commit()

    def load_yaml_schema(self, ymlfn):
        """load yaml file and store the schema in DbSchema"""
        self.L.debug("load_yaml_schema: %s", ymlfn)
        with open(ymlfn) as fh:
            rv = yaml.safe_load(fh.read())
        self.DbSchema = rv
        assert rv.get('tables') != None
        return rv

    def create_tables(self, force = False):
        """returns a list of SQL commands that creates all tables given in the schema"""
        commands = []
        for tdescr in self.DbSchema.get("tables", []):
            if force:
                cmd = "DROP TABLE IF EXISTS `%s`;" % tdescr['name']
                commands.append(cmd)
            colspec = ["%s %s %s" % (col['field'], col['type'], col.get('default', '')) for col in tdescr['columns']]
            cmd = "CREATE TABLE IF NOT EXISTS `%s`\n" % tdescr['name']
            cmd += "(\n   " + ",\n   ".join(colspec) + '\n);'
            commands.append(cmd)
        self.L.debug("create table commands:\n - %s", "\n - ".join(commands))
        return commands

    def get_field_names(self):
        """returns dicitionary of all tables and their fieldnames"""
        rv= {}
        for t in self.DbSchema.get('tables'):
            fields = []
            for c in t['columns']:
                dfl = c.get("default", "****")
                self.L.debug("get_field_names: %s", c)
                if dfl.find("PRIMARY KEY") < 0:
                    fields.append(c['field'])
            rv[t['name']] = fields
        return rv

    # === interface functions =================================================
    def execute_script(self, fn):
        raise Exception("NotImplemented")

    def get_tables(self):
        raise Exception("NotImplemented")

    def query(self, stmt):
        raise Exception("NotImplemented")

    def xquery(self, stmt):
        raise Exception("NotImplemented")

    def commit(self):
        raise Exception("NotImplemented")