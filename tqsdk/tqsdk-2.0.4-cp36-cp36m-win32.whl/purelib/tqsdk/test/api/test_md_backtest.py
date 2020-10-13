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


class TestMdBacktest(unittest.TestCase):
    '''
     行情回测测试
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

    def test_get_quote_backtest(self):
        """
        回测获取行情报价
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_md_backtest_get_quote.script.lzma"))
        # 测试
        try:
            utils.RD = random.Random(4)
            api = TqApi(backtest=TqBacktest(datetime(2020, 6, 2), datetime(2020, 6, 3)),
                        auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
            with closing(api):
                quote = api.get_quote("SHFE.cu2009")
                quote_data = {k: v for k, v in quote.items()}
                quote_data["trading_time"] = {k: v for k, v in quote_data["trading_time"].items()}

                self.assertEqual(json.dumps(quote_data, sort_keys=True),
                                 '{"amount": NaN, "ask_price1": 44640.0, "ask_price2": NaN, "ask_price3": NaN, "ask_price4": NaN, "ask_price5": NaN, "ask_volume1": 1, "ask_volume2": 0, "ask_volume3": 0, "ask_volume4": 0, "ask_volume5": 0, "average": NaN, "bid_price1": 44620.0, "bid_price2": NaN, "bid_price3": NaN, "bid_price4": NaN, "bid_price5": NaN, "bid_volume1": 1, "bid_volume2": 0, "bid_volume3": 0, "bid_volume4": 0, "bid_volume5": 0, "close": NaN, "commission": 12.8525, "datetime": "2020-06-02 00:00:00.000000", "delivery_month": 9, "delivery_year": 2020, "english_name": "ht,hutong,yinjitong", "exchange_id": "SHFE", "expire_datetime": 1600153200.0, "expired": false, "highest": NaN, "ins_class": "FUTURE", "instrument_id": "SHFE.cu2009", "iopv": NaN, "last_price": 44630.0, "lower_limit": NaN, "lowest": NaN, "margin": 17993.5, "max_limit_order_volume": 500, "max_market_order_volume": 0, "min_limit_order_volume": 0, "min_market_order_volume": 0, "mmsa": 1, "open": NaN, "open_interest": 53079, "option_class": "", "pre_close": NaN, "pre_open_interest": 0, "pre_settlement": NaN, "price_decs": 0, "price_tick": 10.0, "product_id": "cu", "product_short_name": "\\u6caa\\u94dc", "quote_multiple": 5.0, "settlement": NaN, "settlement_price": 51410.0, "strike_price": NaN, "trading_day": "20200806", "trading_time": {"day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]], "night": [["21:00:00", "25:00:00"]]}, "underlying_symbol": "", "upper_limit": NaN, "volume": 0, "volume_multiple": 5.0}')                # 其他取值方式
                self.assertNotEqual(quote["pre_close"], quote.pre_close)
                self.assertNotEqual(quote.get("pre_settlement"), quote.pre_settlement)
                self.assertNotEqual(quote.get("highest"), quote.highest)
                self.assertNotEqual(quote.get("lowest"), quote.lowest)
                self.assertNotEqual(quote["open"], quote.open)
                self.assertNotEqual(quote["close"], quote.close)
        except BacktestFinished:
            api.close()
            print("backtest finished")
