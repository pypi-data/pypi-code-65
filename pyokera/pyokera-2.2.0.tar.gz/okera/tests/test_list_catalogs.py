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
#from okera._thrift_api import (TListCatalogsParams)

class ListCatalogsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(ListCatalogsTest, cls).setUpClass()

    def test_list_catalogs(self):
        USER1 = 'okera_employees'
        USER2 = 'restricted'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("create role if not exists temp_role")
            conn.execute_ddl("GRANT ROLE temp_role TO GROUP temp_user")
            conn.execute_ddl("create database if not exists temp_database")
            conn.execute_ddl("""
                grant CREATE_AS_OWNER on database temp_database to role temp_role""")

            # list Catalogs test
            result = conn.list_catalogs(requesting_user='root')
            self.assertTrue(len(result.catalogs) == 1)
            self.assertTrue(result.catalogs[0].name == 'okera')

            # list Catalogs test (for access levels)
            ctx.enable_token_auth(token_str=USER1)
            result = conn.list_catalogs()
            self.assertTrue(len(result.catalogs) == 1)
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                assert 2 in catalog.access_levels
                assert 3 in catalog.access_levels
                assert 5 in catalog.access_levels
                assert 0 not in catalog.access_levels

            # list Catalogs test (No access levels for the user)
            ctx.enable_token_auth(token_str=USER2)
            result = conn.list_catalogs()
            for catalog in result.catalogs:
                self.assertTrue(catalog.name == 'okera')
                self.assertTrue(len(catalog.access_levels) == 0)

if __name__ == "__main__":
    unittest.main()
