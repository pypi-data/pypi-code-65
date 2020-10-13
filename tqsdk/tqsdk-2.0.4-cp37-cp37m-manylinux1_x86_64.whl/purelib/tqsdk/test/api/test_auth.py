#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

import json
import os
import unittest
import random
from contextlib import closing
from datetime import datetime
from tqsdk import TqApi, TqBacktest, BacktestFinished, utils
from tqsdk.test.api.helper import MockServer, MockInsServer
from tqsdk.tools import DataDownloader


class TestAuth(unittest.TestCase):
    '''
     测试对于获取指定类型数据，tqsdk 无权限用户应该给予报错和提示；
     其他测试用例都是使用有全部权限的用户
    '''

    def setUp(self):
        self.ins = MockInsServer(5000)
        os.environ["TQ_INS_URL"] = "http://127.0.0.1:5000/t/md/symbols/2020-08-03.json"
        os.environ["TQ_AUTH_URL"] = "http://127.0.0.1:5000"
        self.mock = MockServer(md_url_character="nfmd")
        self.md_url = "ws://127.0.0.1:5100/"
        self.td_url = "ws://127.0.0.1:5200/"

    def tearDown(self):
        self.ins.close()
        self.mock.close()

    def test_download(self):
        """
        下载数据报错
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_auth_download.script.lzma"))
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin1,tianqin1", _td_url=self.td_url, _md_url=self.md_url)
        self.assertRaises(Exception, DataDownloader, api, symbol_list="CFFEX.T1809", dur_sec=0,
                       start_dt=datetime(2018, 5, 1), end_dt=datetime(2018, 7, 1), csv_file_name="tick.csv")
        api.close()

    def test_backtest(self):
        """
        回测报错
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_md_backtest_get_quote.script.lzma"))
        # 测试
        utils.RD = random.Random(4)
        self.assertRaises(Exception, TqApi, backtest=TqBacktest(datetime(2020, 6, 2), datetime(2020, 6, 3)),
                          auth="tianqin1,tianqin1", _md_url="ws://127.0.0.1:5100/")

    def test_sec(self):
        """
        股票数据
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_auth_sec.script.lzma"))
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin1,tianqin1", _td_url=self.td_url, _md_url=self.md_url)
        self.assertRaises(Exception, api.get_quote, "SSE.10002513")
        api.close()
