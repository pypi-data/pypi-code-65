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
        self.mock = MockServer(md_url_character="nfmd", td_url_character="t-ios.shinnytech.com")
        self.md_url = "ws://127.0.0.1:5100/"
        self.td_url = "ws://127.0.0.1:5200/"

    def tearDown(self):
        self.ins.close()
        self.mock.close()

    def test_risk_rule(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_insert_order_risk.script.lzma"))
        # 测试
        account = TqAccount("N南华期货_ETF", "90101087", "240995")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url) as api:
            symbol = "SSE.10002513"
            quote = api.get_quote(symbol)
            api.set_risk_management_rule("SSE", True)
            risk_data = api.get_risk_management_data(symbol=symbol)
            self.assertEqual(risk_data.user_id, "90101087")
            self.assertEqual(risk_data.exchange_id, "SSE")
            self.assertEqual(risk_data.instrument_id, "10002513")
            self.assertNotEqual(risk_data.self_trade.highest_buy_price, risk_data.self_trade.highest_buy_price)
            self.assertNotEqual(risk_data.self_trade.lowest_sell_price, risk_data.self_trade.lowest_sell_price)
            self.assertEqual(risk_data.self_trade.self_trade_count, 0)
            self.assertEqual(risk_data.self_trade.rejected_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.insert_order_count, 4)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_percent, 0)
            self.assertEqual(risk_data.frequent_cancellation.rejected_count, 0)
            self.assertEqual(risk_data.trade_position_ratio.trade_units, 30)
            self.assertEqual(risk_data.trade_position_ratio.net_position_units, 53)
            self.assertEqual(risk_data.trade_position_ratio.trade_position_ratio, 56.60377358490566)
            self.assertEqual(risk_data.trade_position_ratio.rejected_count, 0)

            order = api.insert_order(symbol=symbol, direction="BUY", offset="OPEN", limit_price=quote.ask_price1,
                                     volume=2, order_id="PYSDK_insert_risk")
            while True:
                api.wait_update()
                if order.status == "FINISHED":
                    break

            self.assertEqual(risk_data.user_id, "90101087")
            self.assertEqual(risk_data.exchange_id, "SSE")
            self.assertEqual(risk_data.instrument_id, "10002513")
            self.assertNotEqual(risk_data.self_trade.highest_buy_price, risk_data.self_trade.highest_buy_price)
            self.assertNotEqual(risk_data.self_trade.lowest_sell_price, risk_data.self_trade.lowest_sell_price)
            self.assertEqual(risk_data.self_trade.self_trade_count, 0)
            self.assertEqual(risk_data.self_trade.rejected_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.insert_order_count, 5)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_percent, 0)
            self.assertEqual(risk_data.frequent_cancellation.rejected_count, 0)
            self.assertEqual(risk_data.trade_position_ratio.trade_units, 40)
            self.assertEqual(risk_data.trade_position_ratio.net_position_units, 63)
            self.assertEqual(risk_data.trade_position_ratio.trade_position_ratio, 63.492063492063494)
            self.assertEqual(risk_data.trade_position_ratio.rejected_count, 0)
