# -*- encoding: utf-8 -*-
'''
@文件    :test_init_environment.py
@说明    :
@时间    :2020/09/02 17:58:36
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import sys
from pprint import pprint
sys.path.append("/data/work/karuoflow")

import unittest
from karuoflow import InitKaruoflowTables
from karuoflow import DbConfig
from karuoflow.db.session import createDbSession
from karuoflow.initflow import InitializeFlowsFromConfigureWithDbConfig
from karuoflow.error_code import KaruoFlowErrors
from karuoflow import KaruoFlow

class InitializeEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.db = createDbSession(DbConfig('localhost', 'duoneng', 'root', 'Ss2018$Ms0802'))
        self.flow_app = KaruoFlow.CreateModel(session=self.db)

    def test_initenv(self):
        self.assertTrue(InitKaruoflowTables('localhost', 3306, 'duoneng', 'root', 'Ss2018$Ms0802'))

    def test_initflowmodel(self):
        InitializeFlowsFromConfigureWithDbConfig("/data/work/karuoflow/examples", 'localhost', 3306, 'duoneng', 'root', 'Ss2018$Ms0802')


    def test_queryflow(self):
        m = self.flow_app.QueryFlow("sealapply")
        self.assertTrue(len(m) > 0)

    def test_queryflowlatest(self):
        m = self.flow_app.QueryLastFlow("sealapply")
        self.assertTrue(len(m) > 0)

    def test_applyflow(self):
        ret_code, job_id = self.flow_app.Apply("sealapply", "caimmy", "我要申请盖章", ext_data={"seal": "**企业法人章"})
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        self.assertLess(0, job_id)

    def test_review_list(self):
        m = self.flow_app.QueryReviewTodoList("caimmy", "sealapply")
        for _item in m:
            self.assertTrue("caimmy" in _item.reviewer)
            self.assertTrue(_item.closed=='0')

        h = self.flow_app.QueryReviewTodoList("caimmy123", "sealapply")
        self.assertEqual(0, len(h))

    def test_all_flowrules(self):
        m = self.flow_app.QueryAllEnabledFlowRules()
        pprint(m)
        self.assertGreater(len(m), 0)

    def test_recall(self):
        ret_code, job_id = self.flow_app.Apply("sealapply", "recaller", "我要申请盖章")
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        h = self.flow_app.Recall(job_id, "recaller")
        self.assertEqual(KaruoFlowErrors.SUCCESS, h)

    def test_examine(self):
        ret_code, job_id = self.flow_app.Apply("sealapply", "recaller", "我要申请盖章")
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        h = self.flow_app.Examine(job_id, "caimmy", True, "同意")
        self.assertEqual(KaruoFlowErrors.SUCCESS, h)
        r = self.flow_app.Examine(job_id, "liudehua", False, "不同意")
        self.assertEqual(KaruoFlowErrors.SUCCESS, r)

    def test_demo(self):
        m = self.flow_app.QueryReviewTodoList("caimmy", "sealapply")
        if len(m) > 0:
            self.flow_app.Examine(m[0].id, "caimmy", True, "adf")

    def test_query_jobinfor(self):
        t = self.flow_app.QueryJob(2)
        pprint(t)

if "__main__" == __name__:
    unittest.main()