# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Some integration tests for auth in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=duplicate-code

import unittest

#from okera import context, _thrift_api
#from datetime import datetime
from okera.tests import pycerebro_test_common as common
#from okera._thrift_api import (TListDatabasesParams)

class ListDatabasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(ListDatabasesTest, cls).setUpClass()

    def test_list_databases(self):
        USER = 'mktg_analyst'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("create role if not exists temp_role")
            conn.execute_ddl("GRANT ROLE temp_role TO GROUP temp_user")
            conn.execute_ddl("create database if not exists temp_database")
            conn.execute_ddl("""
                grant CREATE_AS_OWNER on database temp_database to role temp_role""")
            # list databases test (exact match)
            result = conn.list_databases_v2(exact_names_filter=['demo_test'],
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 1)

            # list databases test (pattern match)
            result = conn.list_databases_v2(name_pattern_filter='*tpc*',
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 10)

            result = conn.list_databases_v2(name_pattern_filter='okera_sample|rs',
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 2)

            # list databases test (no filter criteria)
            result = conn.list_databases_v2()
            self.assertTrue(len(result.databases) == 10)

            # list databases test (very weird pattern. Should return empty list)
            result = conn.list_databases_v2(name_pattern_filter='*WeirdPattern*',
                                            limit=10, page_token=None)
            self.assertTrue(len(result.databases) == 0)

            # list databases test (for access levels)
            ctx.enable_token_auth(token_str=USER)
            result = conn.list_databases_v2(exact_names_filter=['marketing_database'],
                                            limit=10, page_token=None)
            for database in result.databases:
                self.assertTrue(database.name == ['marketing_database'])
                self.assertTrue(database.datasets_count == 3)
                assert 6 in database.access_levels
                assert 3 in database.access_levels
                assert 5 not in database.access_levels
            self.assertTrue(len(result.databases) == 1)

            # list databases test (when there are no tables in the db)
            ctx.enable_token_auth(token_str='temp_user')
            result = conn.list_databases_v2(exact_names_filter=['temp_database'],
                                            limit=10, page_token=None)
            for database in result.databases:
                self.assertTrue(database.name == ['temp_database'])
                self.assertTrue(database.datasets_count == 0)
                assert 6 not in database.access_levels
                assert 3 in database.access_levels
                assert 5 not in database.access_levels
            self.assertTrue(len(result.databases) == 1)

            ctx.enable_token_auth(token_str='root')
            conn.execute_ddl("drop database if exists temp_database")

if __name__ == "__main__":
    unittest.main()
