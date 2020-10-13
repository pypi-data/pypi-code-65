#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: test_td_trade.py
@create_on: 2020/6/12
@description: 
"""
import os
import random
import unittest

from tqsdk import TqApi, TqAccount, utils
from tqsdk.test.api.helper import MockInsServer, MockServer


class TestTdTrade(unittest.TestCase):
    """
    实盘账户下，insert_order 各种情况测试
    """

    def setUp(self):
        self.ins = MockInsServer(5000)
        os.environ["TQ_INS_URL"] = "http://127.0.0.1:5000/t/md/symbols/2020-08-03.json"
        os.environ["TQ_AUTH_URL"] = "http://127.0.0.1:5000"
        self.mock = MockServer(md_url_character="nfmd", td_url_character="q7.htfutures.com")
        self.md_url = "ws://127.0.0.1:5100/"
        self.td_url = "ws://127.0.0.1:5200/"

    def tearDown(self):
        self.ins.close()
        self.mock.close()

    def test_insert_order_shfe_anyprice(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_shfe_anyprice.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        # 测试
        api = TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url, debug=False)
        self.assertRaises(Exception, api.insert_order, "SHFE.au2012", "BUY", "OPEN", 1)
        api.close()

    def test_insert_order_shfe_limit_fok(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_shfe_limit_fok.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url, debug=False) as api:
            order1 = api.insert_order("SHFE.rb2010", "BUY", "OPEN", 2, limit_price=3600, advanced="FOK", order_id="PYSDK_insert_SHFE_limit_FOK1")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_SHFE_limit_FOK1", order1.order_id)
            self.assertEqual("    24590176", order1.exchange_order_id)
            self.assertEqual("SHFE", order1.exchange_id)
            self.assertEqual("rb2010", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(3600.0, order1.limit_price)
            self.assertEqual(1596161626000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("已撤单报单已提交", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_SHFE_limit_FOK1', 'exchange_order_id': '    24590176', 'exchange_id': 'SHFE', 'instrument_id': 'rb2010', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 3600.0, 'price_type': 'LIMIT', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1596161626000000000, 'last_msg': '已撤单报单已提交', 'status': 'FINISHED', 'seqno': 53, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_shfe_limit_fak(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_shfe_limit_fak.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url, debug=False) as api:
            order1 = api.insert_order("SHFE.rb2010", "BUY", "OPEN", 2, limit_price=3600, advanced="FAK", order_id="PYSDK_insert_SHFE_limit_FAK1")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_SHFE_limit_FAK1", order1.order_id)
            self.assertEqual("    24595532", order1.exchange_order_id)
            self.assertEqual("SHFE", order1.exchange_id)
            self.assertEqual("rb2010", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(3600.0, order1.limit_price)
            self.assertEqual(1596161634000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("已撤单报单已提交", order1.last_msg)
            self.assertEqual("{'order_id': 'PYSDK_insert_SHFE_limit_FAK1', 'exchange_order_id': '    24595532', 'exchange_id': 'SHFE', 'instrument_id': 'rb2010', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 3600.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1596161634000000000, 'last_msg': '已撤单报单已提交', 'status': 'FINISHED', 'seqno': 55, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                            str(order1))

    def test_insert_order_dec_best(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dec_best.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        # 测试
        api = TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url, debug=False)
        self.assertRaises(Exception, api.insert_order, "DCE.m2009", "BUY", "OPEN", 1, limit_price="BEST", order_id="PYSDK_insert_DCE_BEST")
        api.close()

    def test_insert_order_dec_fivelevel(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dec_fivelevel.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        # 测试
        api = TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url, debug=False)
        self.assertRaises(Exception, api.insert_order, "DCE.m2009", "BUY", "OPEN", 1, limit_price="FIVELEVEL",
                                          order_id="PYSDK_insert_DCE_FIVELEVEL")
        api.close()

    def test_insert_order_dce_anyprice(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dce_anyprice.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url,
                   debug=False) as api:
            order1 = api.insert_order("DCE.m2009", "BUY", "OPEN", 1, order_id="PYSDK_insert_DCE_any")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_DCE_any", order1.order_id)
            self.assertEqual("    14772806", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2009", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(1, order1.volume_orign)
            self.assertEqual(0, order1.volume_left)
            self.assertEqual(0.0, order1.limit_price)
            self.assertEqual(1596163078000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("ANY", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("全部成交", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_any', 'exchange_order_id': '    14772806', 'exchange_id': 'DCE', 'instrument_id': 'm2009', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': 0.0, 'price_type': 'ANY', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1596163078000000000, 'last_msg': '全部成交', 'status': 'FINISHED', 'seqno': 60, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_anyprice_fok(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dce_anyprice_fok.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url,
                   debug=False) as api:
            order1 = api.insert_order("DCE.m2009", "BUY", "OPEN", 2, advanced="FOK", order_id="PYSDK_insert_DCE_any_FOK")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_DCE_any_FOK", order1.order_id)
            self.assertEqual("    14929008", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2009", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(0, order1.volume_left)
            self.assertEqual(0.0, order1.limit_price)
            self.assertEqual(1596163482000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("ANY", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("全部成交", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_any_FOK', 'exchange_order_id': '    14929008', 'exchange_id': 'DCE', 'instrument_id': 'm2009', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 0, 'limit_price': 0.0, 'price_type': 'ANY', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1596163482000000000, 'last_msg': '全部成交', 'status': 'FINISHED', 'seqno': 68, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fak(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fak.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url,
                   debug=False) as api:
            order1 = api.insert_order("DCE.m2009", "SELL", "OPEN", 2, limit_price=2800, advanced="FAK", order_id="PYSDK_insert_DCE_limit_FAK1")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_DCE_limit_FAK1", order1.order_id)
            self.assertEqual("    15096108", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2009", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(0, order1.volume_left)
            self.assertEqual(2800.0, order1.limit_price)
            self.assertEqual(1596163955000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("全部成交", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FAK1', 'exchange_order_id': '    15096108', 'exchange_id': 'DCE', 'instrument_id': 'm2009', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 0, 'limit_price': 2800.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1596163955000000000, 'last_msg': '全部成交', 'status': 'FINISHED', 'seqno': 82, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fok(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fok.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url,
                   debug=False) as api:
            order1 = api.insert_order("DCE.m2009", "SELL", "OPEN", 2, limit_price=2800, advanced="FOK", order_id="PYSDK_insert_DCE_limit_FOK")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_limit_FOK", order1.order_id)
            self.assertEqual("    15220256", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2009", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(0, order1.volume_left)
            self.assertEqual(2800.0, order1.limit_price)
            self.assertEqual(1596164382000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("全部成交", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FOK', 'exchange_order_id': '    15220256', 'exchange_id': 'DCE', 'instrument_id': 'm2009', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 0, 'limit_price': 2800.0, 'price_type': 'LIMIT', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1596164382000000000, 'last_msg': '全部成交', 'status': 'FINISHED', 'seqno': 90, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fak1(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fak1.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url,
                   debug=False) as api:
            order1 = api.insert_order("DCE.m2009", "BUY", "OPEN", 2, limit_price=2890, advanced="FAK", order_id="PYSDK_insert_DCE_limit_FAK2")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_DCE_limit_FAK2", order1.order_id)
            self.assertEqual("    15326041", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2009", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(2890.0, order1.limit_price)
            self.assertEqual(1596164694000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("已撤单", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FAK2', 'exchange_order_id': '    15326041', 'exchange_id': 'DCE', 'instrument_id': 'm2009', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 2890.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1596164694000000000, 'last_msg': '已撤单', 'status': 'FINISHED', 'seqno': 98, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fok1(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fok1.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha121212")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=self.md_url, _td_url=self.td_url,
                   debug=False) as api:
            order1 =  api.insert_order("DCE.m2009", "SELL", "OPEN", 2, limit_price=2985, advanced="FOK", order_id="PYSDK_insert_DCE_limit_FOK1")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_limit_FOK1", order1.order_id)
            self.assertEqual("    15330855", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2009", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(2985.0, order1.limit_price)
            self.assertEqual(1596164705000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("已撤单", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FOK1', 'exchange_order_id': '    15330855', 'exchange_id': 'DCE', 'instrument_id': 'm2009', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 2985.0, 'price_type': 'LIMIT', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1596164705000000000, 'last_msg': '已撤单', 'status': 'FINISHED', 'seqno': 101, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))
