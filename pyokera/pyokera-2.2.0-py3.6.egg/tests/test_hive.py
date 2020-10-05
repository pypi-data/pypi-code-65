# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Some integration tests for hive in PyOkera
#
# pylint: disable=logging-not-lazy
# pylint: disable=no-self-use
# pylint: disable=no-else-return
import os
import unittest

from pyhive import hive
from okera.tests import pycerebro_test_common as common
from okera.tests import _mr_util as mr_util
from okera._util import get_logger_and_init_null

DEFAULT_HIVE_HOST = os.environ['ODAS_TEST_HOST']
DEFAULT_HIVE_PORT = int(os.environ['ODAS_TEST_PORT_HIVESERVER2'])
IS_AUTHORIZE_QUERY = common.get_bool_env_var('OKERA_ENABLE_AUTHORIZE_QUERY', False)

_log = get_logger_and_init_null(__name__)

blacklisted_dbs = [
    'delta_db',
]

# blacklist tables that we do not support scanning via hive. revisit.
blacklisted_tbls = [
    'bad_metadata_db.broken_view',
    'chase.redacted_ledger_balance_view',
    'chase.cte_view',
    'customer.zd608_fiducia_risk_score_ato_tb',
    'demo_test.transactions_anonymize_inactive_users_external_view',
    'okera_system.configs',
    'okera_system.events_by_user_dataset_tags',
    'okera_system.fs_events_by_client_ip_tagged',
    'okera_system.fs_events_by_hour_tags',
    'okera_system.fs_events_by_user_dataset_tags',
    'okera_system.steward_fs_tagged_audit_logs',
    'okera_system.steward_fs_tagged_audit_logs_preview',
    'partition_test.timestamp_part_encoded',
    'partition_test.timestamp_part_test',
    'partition_test.weird_partition2',
    'partition_test.weird_partition3',
    'partition_test.weird_partition4',
    'partition_test.weird_partition5',
    'partition_test.weird_partition6',
    'partition_test.weird_partition7',
    'partition_test.weird_partition8',
    'rs.partitioned_alltypes',
    'special_chars.test_table',

    # Non standard partition files. Its bizzare that the hudi_partitioned table failed!
    'rs_complex_parquet.hudi_partitioned',
    'rs_complex_parquet.hudi_nonpartitioned',
    'rs_complex_parquet.hudi_as_parquet',
]

# Authorize query has some limitations right now, so skip these additional tables
authorize_query_blacklisted_tbls = [
    # Generated query as duplicate column names
    'authdb.struct_t_full_view_on_sel_complex_view',
    'authdb.struct_t_sel_view_on_sel_complex_view',
    'authdb.struct_t_view_on_view',
    'customer.market_decide_offer_decision_v3_card_non_npi_vw',
    'okera_system.events_by_hour',
    'okera_system.events_by_user_dataset',
    'rs_complex.struct_nested_s1_s2',
    'rs_complex_parquet.struct_nested_s1_s2',

    # Something else is wrong
    'buckets_test.spark_bucketed_test_view',

    # Missing less relevant out of box UDFs
    'okera_system.daily_reporting_audit_logs',
    'okera_system.fs_events_by_client_ip',
    'okera_system.fs_events_by_hour',
    'okera_system.fs_events_by_user_dataset',
    'okera_system.reporting_audit_logs',
] + mr_util.authorize_query_unsupported_datasets

def skip_table(tbl_name):
    if tbl_name in blacklisted_tbls:
        return True
    if IS_AUTHORIZE_QUERY and tbl_name in authorize_query_blacklisted_tbls:
        return True
    return False

class HiveScanTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(HiveScanTest, cls).setUpClass()
        cls._conn = hive.Connection(host=DEFAULT_HIVE_HOST,
                                    port=DEFAULT_HIVE_PORT, username="root")
        cls._cursor = cls._conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls._cursor.close()
        cls._conn.close()

    def __describe(self, tbl):
        self._cursor.execute('DESCRIBE FORMATTED %s' % tbl)
        return '\n'.join([str(s) for s in self._cursor.fetchall()])

    def __explain(self, tbl):
        self._cursor.execute('EXPLAIN SELECT * FROM %s' % tbl)
        return '\n'.join([str(s) for s in self._cursor.fetchall()])

    def __query_first_row(self, sql):
        self._cursor.execute(sql)
        return self._cursor.fetchall()[0]

    @unittest.skipIf(not IS_AUTHORIZE_QUERY, "Skipping, authorize query is disabled.")
    def test_show_okera_udfs(self):
        self._cursor.execute("SHOW FUNCTIONS like 'default.*'")
        rows = self._cursor.fetchall()
        udfs = []
        for row in rows:
            udfs.append(row[0])
        print(udfs)
        self.assertTrue('default.mask' in udfs)
        self.assertTrue('default.mask_ccn' in udfs)
        self.assertTrue('default.null' in udfs)
        self.assertTrue('default.sha2' in udfs)
        self.assertTrue('default.tokenize' in udfs)
        self.assertTrue('default.zero' in udfs)

    @unittest.skipIf(not IS_AUTHORIZE_QUERY, "Skipping, authorize query is disabled.")
    def test_okera_udfs(self):
        self.assertEqual('xxxx', self.__query_first_row("select mask('abcd')")[0])
        self.assertEqual(
            'XXXX-efgh',
            self.__query_first_row("select mask_ccn('abcd-efgh')")[0])
        self.assertEqual(None, self.__query_first_row("select `null`('abcd')")[0])
        self.assertEqual(
            267444780464769297,
            self.__query_first_row("select default.sha2('abcd')")[0])
        self.assertTrue(self.__query_first_row("select tokenize('abcd')")[0] != 'abcd')
        self.assertEqual('', self.__query_first_row("select zero('abcd')")[0])

    def test_show_databases(self):
        self._cursor.execute('SHOW DATABASES')
        rows = self._cursor.fetchall()
        dbFound = False
        for row in rows:
            if 'okera_sample' in row:
                dbFound = True
                break
        self.assertTrue(dbFound)

    def test_show_tables(self):
        self._cursor.execute('SHOW DATABASES')
        dbs = self._cursor.fetchall()
        for db in dbs:
            if not db[0].startswith('_'):
                self._cursor.execute('SHOW TABLES IN ' + db[0])

    def test_select_singlerow(self):
        tables_scanned = 0
        self._cursor.execute('SHOW DATABASES')
        dbs = self._cursor.fetchall()
        for db in dbs:
            db = db[0]
            if db.startswith('_') or db in blacklisted_dbs:
                continue

            self._cursor.execute('SHOW TABLES IN ' + db)
            tbls = self._cursor.fetchall()
            for tbl in tbls:
                full_tbl_name = db + '.' + tbl[0]
                if tbl[0].startswith('_') or skip_table(full_tbl_name):
                    continue
                tables_scanned += 1
                sql = 'SELECT * FROM ' + full_tbl_name + ' LIMIT 1'
                print("Hive::test_select_singlerow SQL: " + sql)
                self._cursor.execute(sql)
        _log.info("Total tables scanned: %d" % tables_scanned)

    @unittest.skipIf(not IS_AUTHORIZE_QUERY, "Skipping, authorize query is disabled.")
    def test_explain(self):
        whoami = self.__describe('okera_sample.whoami')
        self.assertTrue("SELECT 'root' as `user`" in whoami)
        whoami = self.__explain('okera_sample.whoami')
        self.assertTrue("alias: _dummy_table" in whoami)
        self.assertTrue("expressions: 'root'" in whoami)

        users_ccn_masked = self.__describe('okera_sample.users_ccn_masked')
        self.assertTrue("default.`mask_ccn`(`ccn`) FROM" in users_ccn_masked)

        alltypes_s3 = self.__describe('rs.alltypes_s3')
        self.assertTrue("s3a://cerebrodata-test/alltypes" in alltypes_s3)
        self.assertTrue("org.apache.hadoop.mapred.TextInputFormat" in alltypes_s3)
        alltypes_s3 = self.__explain('rs.alltypes_s3')
        self.assertTrue("alias: alltypes_s3" in alltypes_s3)
        self.assertTrue("expressions: bool_col (type: boolean)" in alltypes_s3)
