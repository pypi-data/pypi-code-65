#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import os
import random
import unittest
from tqsdk.test.api.helper import MockInsServer, MockServer
from tqsdk import TqApi, utils


class TestTdBasic(unittest.TestCase):
    """
    测试TqApi交易相关函数基本功能, 以及TqApi与交易服务器交互是否符合设计预期

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 utils.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

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

    # 模拟交易测试

    # @unittest.skip("无条件跳过")
    def test_insert_order(self):
        """
        下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_simulate.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("DCE.jd2009", "BUY", "OPEN", 1)
        order2 = api.insert_order("SHFE.cu2008", "BUY", "OPEN", 2, limit_price=52800)

        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()

        self.assertEqual(order1.order_id, "PYSDK_insert_8ca5996666ceab360512bd1311072231")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 1)
        self.assertEqual(order1.volume_left, 0)
        self.assertNotEqual(order1.limit_price, order1.limit_price)  # 判断nan
        self.assertEqual(order1.price_type, "ANY")
        self.assertEqual(order1.volume_condition, "ANY")
        self.assertEqual(order1.time_condition, "IOC")
        self.assertAlmostEqual(1595987228432530000 / 1e9, order1.insert_date_time / 1e9, places=1)
        self.assertEqual(order1.status, "FINISHED")
        for k, v in order1.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1595987228432922000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_id': 'DCE', 'instrument_id': 'jd2009', 'direction': 'BUY', 'offset': 'OPEN', 'price': 4172, 'volume': 1, 'user_id': 'TQSIM', 'commission': 6.2685}")

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "BUY")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 52800.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ANY")
        self.assertEqual(order2.time_condition, "GFD")
        self.assertAlmostEqual(1595987228434286000 / 1e9, order2.insert_date_time / 1e9, places=1)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order2.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1595987228434662000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2008', 'direction': 'BUY', 'offset': 'OPEN', 'price': 52800.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 25.88}")
        api.close()

    def test_insert_order_fok(self):
        """
        下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_fok_simulate.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容

        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("SHFE.au2012", "BUY", "OPEN", 2, limit_price=419, advanced="FOK")
        order2 = api.insert_order("SHFE.cu2008", "BUY", "OPEN", 2, limit_price=52800, advanced="FOK")
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()

        self.assertEqual(order1.order_id, "PYSDK_insert_8ca5996666ceab360512bd1311072231")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 2)
        self.assertEqual(order1.volume_left, 2)
        self.assertEqual(order1.limit_price, 419.0)  # 判断nan
        self.assertEqual(order1.price_type, "LIMIT")
        self.assertEqual(order1.volume_condition, "ALL")
        self.assertEqual(order1.time_condition, "IOC")
        self.assertAlmostEqual(1595987248005787000 / 1e9, order1.insert_date_time / 1e9, places=1)
        self.assertEqual(order1.status, "FINISHED")
        self.assertEqual(len(order1.trade_records.items()), 0)  # 没有成交记录

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "BUY")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 52800.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ALL")
        self.assertEqual(order2.time_condition, "IOC")
        self.assertAlmostEqual(1595987248008686000 / 1e9, order2.insert_date_time / 1e9, places=1)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order2.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1595987248008991000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2008', 'direction': 'BUY', 'offset': 'OPEN', 'price': 52800.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 25.88}")

        api.close()

    def test_insert_order_fak(self):
        """
        下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_fak_simulate.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容

        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("SHFE.au2012", "BUY", "OPEN", 2, limit_price=419, advanced="FAK")
        order2 = api.insert_order("SHFE.cu2008", "BUY", "OPEN", 2, limit_price=52800, advanced="FAK")
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        self.assertEqual(order1.order_id, "PYSDK_insert_8ca5996666ceab360512bd1311072231")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 2)
        self.assertEqual(order1.volume_left, 2)
        self.assertEqual(order1.limit_price, 419.0)  # 判断nan
        self.assertEqual(order1.price_type, "LIMIT")
        self.assertEqual(order1.volume_condition, "ANY")
        self.assertEqual(order1.time_condition, "IOC")
        self.assertAlmostEqual(1595987267505561000 / 1e9, order1.insert_date_time / 1e9, places=1)
        self.assertEqual(order1.status, "FINISHED")
        self.assertEqual(len(order1.trade_records.items()), 0)  # 没有成交记录

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "BUY")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 52800.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ANY")
        self.assertEqual(order2.time_condition, "IOC")
        self.assertAlmostEqual(1595987267506702000 / 1e9, order2.insert_date_time / 1e9, places=1)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order1.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1595987267506958000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2008', 'direction': 'BUY', 'offset': 'OPEN', 'price': 52800.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 25.84}")
        api.close()

    def test_cancel_order(self):
        """
        撤单

        注：本函数不是回测，重新在盘中生成测试用例script文件时更改为当前可交易的合约代码,且_ins_url可能需修改。
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_cancel_order_simulate.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("DCE.jd2009", "BUY", "OPEN", 1, limit_price=4010)
        order2 = api.insert_order("SHFE.cu2008", "BUY", "OPEN", 2, limit_price=41900)
        api.wait_update()

        self.assertEqual("ALIVE", order1.status)
        self.assertEqual("ALIVE", order2.status)

        api.cancel_order(order1)
        api.cancel_order(order2.order_id)
        while order1.status != "FINISHED" or order2.status != "FINISHED":
            api.wait_update()

        self.assertEqual("FINISHED", order1.status)
        self.assertEqual("FINISHED", order2.status)
        self.assertNotEqual(order1.volume_left, 0)
        self.assertNotEqual(order2.volume_left, 0)

        api.close()

    def test_get_account(self):
        """
        获取账户资金信息
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_account_simulate.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order = api.insert_order("DCE.jd2009", "BUY", "OPEN", 1, limit_price=4220)
        while order.status == "ALIVE":
            api.wait_update()
        account = api.get_account()
        print(str(account))
        # 测试脚本重新生成后，数据根据实际情况有变化
        self.assertEqual(str(account),
                         "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9999563.7315, 'available': 9996638.431499999, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -430.0, 'position_profit': -430.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 2925.3, 'frozen_commission': 0.0, 'commission': 6.2685, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.00029254276271922775, 'market_value': 0.0}")
        self.assertEqual(account.currency, "CNY")
        self.assertEqual(account.pre_balance, 10000000.0)
        self.assertEqual(9999563.7315, account.balance)
        self.assertEqual(6.2685, account["commission"])
        self.assertEqual(2925.3, account["margin"])
        self.assertEqual(-430.0, account.position_profit)
        api.close()

    def test_get_position(self):
        """
        获取持仓
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_position_simulate.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("DCE.jd2009", "BUY", "OPEN", 1, limit_price=4220)
        order2 = api.insert_order("DCE.jd2009", "BUY", "OPEN", 3)
        order3 = api.insert_order("DCE.jd2009", "SELL", "OPEN", 3)
        while order1.status == "ALIVE" or order2.status == "ALIVE" or order3.status == "ALIVE":
            api.wait_update()
        position = api.get_position("DCE.jd2009")
        # 测试脚本重新生成后，数据根据实际情况有变化
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'jd2009', 'pos_long_his': 0, 'pos_long_today': 4, 'pos_short_his': 0, 'pos_short_today': 3, 'volume_long_today': 4, 'volume_long_his': 0, 'volume_long': 4, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 3, 'volume_short_his': 0, 'volume_short': 3, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 4187.75, 'open_price_short': 4176.0, 'open_cost_long': 167510.0, 'open_cost_short': 125280.0, 'position_price_long': 4187.75, 'position_price_short': 4176.0, 'position_cost_long': 167510.0, 'position_cost_short': 125280.0, 'float_profit_long': -470.0, 'float_profit_short': 0.0, 'float_profit': -470.0, 'position_profit_long': -470.0, 'position_profit_short': 0.0, 'position_profit': -470.0, 'margin_long': 11701.2, 'margin_short': 8775.900000000001, 'margin': 20477.100000000002, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 4176}",
            str(position))
        self.assertEqual(1, position.pos)
        self.assertEqual(4, position.pos_long)
        self.assertEqual(3, position.pos_short)
        self.assertEqual(position.exchange_id, "DCE")
        self.assertEqual(position.instrument_id, "jd2009")
        self.assertEqual(position.pos_long_his, 0)
        self.assertEqual(position.pos_long_today, 4)
        self.assertEqual(position.pos_short_his, 0)
        self.assertEqual(position.pos_short_today, 3)
        self.assertEqual(position.volume_long_today, 4)
        self.assertEqual(position.volume_long_his, 0)
        self.assertEqual(position.volume_long, 4)
        self.assertEqual(position.volume_long_frozen_today, 0)
        self.assertEqual(position.volume_long_frozen_his, 0)
        self.assertEqual(position.volume_long_frozen, 0)
        self.assertEqual(position.volume_short_today, 3)
        self.assertEqual(position.volume_short_his, 0)
        self.assertEqual(position.volume_short, 3)
        self.assertEqual(position.volume_short_frozen_today, 0)
        self.assertEqual(position.volume_short_frozen_his, 0)
        self.assertEqual(position.volume_short_frozen, 0)
        self.assertEqual(position.open_price_long, 4187.75)
        self.assertEqual(position.open_price_short, 4176.0)
        self.assertEqual(position.open_cost_long, 167510.0)
        self.assertEqual(position.open_cost_short, 125280.0)
        self.assertEqual(position.position_price_long, 4187.75)
        self.assertEqual(position.position_price_short, 4176.0)
        self.assertEqual(position.position_cost_long, 167510.0)
        self.assertEqual(position.position_cost_short, 125280.0)
        self.assertEqual(position.float_profit_long, -470.0)
        self.assertEqual(position.float_profit_short, 0.0)
        self.assertEqual(position.float_profit, -470.0)
        self.assertEqual(position.position_profit_long, -470.0)
        self.assertEqual(position.position_profit_short, 0.0)
        self.assertEqual(position.position_profit, -470.0)
        self.assertEqual(position.margin_long, 11701.2)
        self.assertEqual(position.margin_short, 8775.900000000001)
        self.assertEqual(position.margin, 20477.100000000002)
        self.assertEqual(position.market_value_long, 0.0)
        self.assertEqual(position.market_value_short, 0.0)
        self.assertEqual(position.market_value, 0.0)
        self.assertEqual(position.last_price, 4176.0)

        # 其他取值方式测试
        self.assertEqual(position["pos_long_today"], 4)
        self.assertEqual(position["pos_short_today"], 3)
        self.assertEqual(position["volume_long_his"], 0)
        self.assertEqual(position["volume_long"], 4)

        api.close()

    def test_get_trade(self):
        """
        获取成交记录
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_trade_simulate.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("DCE.jd2009", "BUY", "OPEN", 1)
        order2 = api.insert_order("SHFE.cu2010", "BUY", "OPEN", 2, limit_price=52800)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()

        trade1 = api.get_trade("PYSDK_insert_8ca5996666ceab360512bd1311072231|1")
        trade2 = api.get_trade("PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2")
        self.assertAlmostEqual(1595987343435094000 / 1e9, trade1.trade_date_time / 1e9, places=1)
        self.assertAlmostEqual(1595987343438064000 / 1e9, trade2.trade_date_time / 1e9, places=1)
        del trade1["trade_date_time"]
        del trade2["trade_date_time"]
        self.assertEqual(str(trade1),
                         "{'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_id': 'DCE', 'instrument_id': 'jd2009', 'direction': 'BUY', 'offset': 'OPEN', 'price': 4176, 'volume': 1, 'user_id': 'TQSIM', 'commission': 6.2685}")
        self.assertEqual(str(trade2),
                         "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2010', 'direction': 'BUY', 'offset': 'OPEN', 'price': 52800.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 25.825}")
        self.assertEqual(trade1.direction, "BUY")
        self.assertEqual(trade1.offset, "OPEN")
        self.assertEqual(trade1.price, 4176.0)
        self.assertEqual(trade1.volume, 1)
        self.assertEqual(trade1.commission, 6.2685)

        self.assertEqual(trade2.direction, "BUY")
        self.assertEqual(trade2.offset, "OPEN")
        self.assertEqual(trade2.price, 52800.0)
        self.assertEqual(trade2.volume, 2)
        self.assertEqual(trade2.commission, 25.825)
        api.close()

    def test_get_order(self):
        """
        获取委托单信息
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_order_simulate.script.lzma"))
        # 测试: 模拟账户下单
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("DCE.jd2009", "BUY", "OPEN", 1)
        order2 = api.insert_order("SHFE.cu2010", "SELL", "OPEN", 2, limit_price=41900)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()

        get_order1 = api.get_order(order1.order_id)
        get_order2 = api.get_order(order2.order_id)

        self.assertEqual(get_order1.order_id, "PYSDK_insert_8ca5996666ceab360512bd1311072231")
        self.assertEqual(get_order1.direction, "BUY")
        self.assertEqual(get_order1.offset, "OPEN")
        self.assertEqual(get_order1.volume_orign, 1)
        self.assertEqual(get_order1.volume_left, 0)
        self.assertNotEqual(get_order1.limit_price, get_order1.limit_price)  # 判断nan
        self.assertEqual(get_order1.price_type, "ANY")
        self.assertEqual(get_order1.volume_condition, "ANY")
        self.assertEqual(get_order1.time_condition, "IOC")
        # 因为TqSim模拟交易的 insert_date_time 不是固定值，所以改为判断范围（前后100毫秒）
        self.assertAlmostEqual(1595987361948827000 / 1e9, get_order1.insert_date_time / 1e9, places=1)
        self.assertEqual(get_order1.last_msg, "全部成交")
        self.assertEqual(get_order1.status, "FINISHED")
        self.assertEqual(get_order1.frozen_margin, 0)

        self.assertEqual(get_order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(get_order2.direction, "SELL")
        self.assertEqual(get_order2.offset, "OPEN")
        self.assertEqual(get_order2.volume_orign, 2)
        self.assertEqual(get_order2.volume_left, 0)
        self.assertEqual(get_order2.limit_price, 41900.0)
        self.assertEqual(get_order2.price_type, "LIMIT")
        self.assertEqual(get_order2.volume_condition, "ANY")
        self.assertEqual(get_order2.time_condition, "GFD")
        self.assertAlmostEqual(1595987361949641000 / 1e9, get_order2["insert_date_time"] / 1e9, places=1)
        self.assertEqual(get_order2["last_msg"], "全部成交")
        self.assertEqual(get_order2["status"], "FINISHED")
        self.assertEqual(get_order2.frozen_margin, 0)

        del get_order1["insert_date_time"]
        del get_order2["insert_date_time"]
        self.assertEqual(str(get_order1),
                         "{'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'exchange_order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'exchange_id': 'DCE', 'instrument_id': 'jd2009', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': nan, 'price_type': 'ANY', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}")
        self.assertEqual(str(get_order2),
                         "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_id': 'SHFE', 'instrument_id': 'cu2010', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 0, 'limit_price': 41900.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}")

        api.close()

    # 期权模拟交易盘中测试

    def test_insert_order_option(self):
        """
            期权下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file",
                                   "test_td_basic_insert_order_simulate_option.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("SHFE.cu2009C47000", "BUY", "OPEN", 1, limit_price=5400)
        order2 = api.insert_order("CZCE.SR101C5200", "SELL", "OPEN", 2, limit_price=70)
        order3 = api.insert_order("DCE.m2101-P-2900", "BUY", "OPEN", 3, limit_price=120)
        while order1.status == "ALIVE" or order2.status == "ALIVE" or order3.status == "ALIVE":
            api.wait_update()

        self.assertEqual(order1.order_id, "PYSDK_insert_8ca5996666ceab360512bd1311072231")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 1)
        self.assertEqual(order1.volume_left, 0)
        self.assertEqual(order1.limit_price, 5400.0)
        self.assertEqual(order1.price_type, "LIMIT")
        self.assertEqual(order1.volume_condition, "ANY")
        self.assertEqual(order1.time_condition, "GFD")
        self.assertAlmostEqual(1596770380399218000 / 1e9, order1.insert_date_time / 1e9, places=1)
        self.assertEqual(order1.status, "FINISHED")
        for k, v in order1.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1596770380399459000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_id': 'SHFE', 'instrument_id': 'cu2009C47000', 'direction': 'BUY', 'offset': 'OPEN', 'price': 5400.0, 'volume': 1, 'user_id': 'TQSIM', 'commission': 10}")

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "SELL")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 70.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ANY")
        self.assertEqual(order2.time_condition, "GFD")
        self.assertAlmostEqual(1596770380398285000 / 1e9, order2.insert_date_time / 1e9, places=1)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order2.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1596770380398589000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'CZCE', 'instrument_id': 'SR101C5200', 'direction': 'SELL', 'offset': 'OPEN', 'price': 70.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 20}")

        self.assertEqual(order3.order_id, "PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258")
        self.assertEqual(order3.direction, "BUY")
        self.assertEqual(order3.offset, "OPEN")
        self.assertEqual(order3.volume_orign, 3)
        self.assertEqual(order3.volume_left, 0)
        self.assertEqual(order3.limit_price, 120.0)
        self.assertEqual(order3.price_type, "LIMIT")
        self.assertEqual(order3.volume_condition, "ANY")
        self.assertEqual(order3.time_condition, "GFD")
        self.assertAlmostEqual(1596770380399663000 / 1e9, order3.insert_date_time / 1e9, places=1)
        self.assertEqual(order3.status, "FINISHED")
        for k, v in order3.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1596770380399869000 / 1e9, v.trade_date_time / 1e9, places=1)
            del v.trade_date_time
            self.assertEqual(str(v),
                             "{'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'trade_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258|3', 'exchange_trade_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258|3', 'exchange_id': 'DCE', 'instrument_id': 'm2101-P-2900', 'direction': 'BUY', 'offset': 'OPEN', 'price': 120.0, 'volume': 3, 'user_id': 'TQSIM', 'commission': 30}")

        api.close()

    def test_cancel_order_option1(self):
        """
            撤单
            注：本函数不是回测，重新盘中生成测试用例script文件时更改为当前可交易的合约代码,且_ins_url可能需修改。
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_cancel_order_simulate_option1.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("DCE.m2009-P-2900", "BUY", "OPEN", 1, limit_price=15)
        api.wait_update()
        self.assertEqual("ALIVE", order1.status)
        api.cancel_order(order1)
        while order1.status != "FINISHED":
            api.wait_update()
        self.assertEqual("FINISHED", order1.status)
        self.assertNotEqual(order1.volume_left, 0)
        api.close()

    def test_cancel_order_option2(self):
        """
            撤单
            注：本函数不是回测，重新盘中生成测试用例script文件时更改为当前可交易的合约代码,且_ins_url可能需修改。
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_cancel_order_simulate_option2.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order2 = api.insert_order("SHFE.cu2008C47000", "BUY", "OPEN", 2, limit_price=4200)
        api.wait_update()
        self.assertEqual("ALIVE", order2.status)
        api.cancel_order(order2.order_id)
        while order2.status != "FINISHED":
            api.wait_update()
        self.assertEqual("FINISHED", order2.status)
        self.assertNotEqual(order2.volume_left, 0)
        api.close()

    def test_get_account_option(self):
        """
            获取账户资金信息
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_account_simulate_option.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url, debug="debug.log")
        order1 = api.insert_order("CZCE.SR101C5200", "SELL", "OPEN", 2, limit_price=7)
        order2 = api.insert_order("DCE.m2009-P-2900", "BUY", "OPEN", 3, limit_price=100)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        account = api.get_account()
        # 测试脚本重新生成后，数据根据实际情况有变化
        print(str(account))
        self.assertEqual(str(account),
                         "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9995740.0, 'available': 9990754.4, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -4070.0, 'position_profit': 0.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 6195.599999999999, 'frozen_commission': 0.0, 'commission': 50.0, 'frozen_premium': 0.0, 'premium': -3000.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0006198240450431883, 'market_value': -1210.0}")
        self.assertEqual(account.currency, "CNY")
        self.assertEqual(account.pre_balance, 10000000.0)
        self.assertEqual(account.balance, 9995740.0)
        self.assertEqual(account["commission"], 50.0)
        self.assertEqual(account["margin"], 6195.599999999999)
        self.assertEqual(account.position_profit, 0.0)
        self.assertEqual(account.available, 9990754.4)
        self.assertNotEqual(account.ctp_balance, account.ctp_balance)  # nan
        self.assertEqual(account.float_profit, -4070.0)
        self.assertEqual(account.position_profit, 0.0)
        self.assertEqual(account.margin, 6195.599999999999)
        self.assertEqual(account.commission, 50.0)
        self.assertEqual(account.premium, -3000.0)
        self.assertEqual(account.risk_ratio, 0.0006198240450431883)
        self.assertEqual(account.market_value, -1210.0)
        api.close()

    def test_get_position_option(self):
        """
            获取持仓
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_position_simulate_option.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("CZCE.SR101C5200", "BUY", "OPEN", 2, limit_price=160)
        order2 = api.insert_order("CZCE.SR101C5200", "BUY", "OPEN", 3, limit_price=160)
        order3 = api.insert_order("CZCE.SR101C5200", "SELL", "OPEN", 3, limit_price=80)
        order4 = api.insert_order("CZCE.SR101C5200", "SELL", "OPEN", 3)  # 只有郑商所支持期权市价单
        self.assertRaises(Exception, api.insert_order, "DCE.m2009-P-2900", "BUY", "OPEN", 1) # 只有郑商所支持期权市价单

        while order1.status == "ALIVE" or order2.status == "ALIVE" or order3.status == "ALIVE" or order4.status == "ALIVE":
            api.wait_update()
        self.assertEqual(order4.volume_left, 0)
        position = api.get_position("CZCE.SR101C5200")
        position2 = api.get_position("DCE.m2009-P-2900")
        self.assertEqual(0, position2.pos_long)
        self.assertEqual(0, position2.pos_short)

        # 测试脚本重新生成后，数据根据实际情况有变化
        self.assertEqual(str(position),
                         "{'exchange_id': 'CZCE', 'instrument_id': 'SR101C5200', 'pos_long_his': 0, 'pos_long_today': 5, 'pos_short_his': 0, 'pos_short_today': 6, 'volume_long_today': 5, 'volume_long_his': 0, 'volume_long': 5, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 6, 'volume_short_his': 0, 'volume_short': 6, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 160.0, 'open_price_short': 117.5, 'open_cost_long': 8000.0, 'open_cost_short': 7050.0, 'position_price_long': 160.0, 'position_price_short': 117.5, 'position_cost_long': 8000.0, 'position_cost_short': 7050.0, 'float_profit_long': -100.0, 'float_profit_short': -2430.0, 'float_profit': -2530.0, 'position_profit_long': 0.0, 'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 12996.800000000001, 'margin': 12996.800000000001, 'market_value_long': 7900.0, 'market_value_short': -9480.0, 'market_value': -1580.0, 'last_price': 158.0}")
        self.assertEqual(-1, position.pos)
        self.assertEqual(5, position.pos_long)
        self.assertEqual(6, position.pos_short)
        self.assertEqual(position.exchange_id, "CZCE")
        self.assertEqual(position.instrument_id, "SR101C5200")
        self.assertEqual(position.pos_long_his, 0)
        self.assertEqual(position.pos_long_today, 5)
        self.assertEqual(position.pos_short_his, 0)
        self.assertEqual(position.pos_short_today, 6)
        self.assertEqual(position.volume_long_today, 5)
        self.assertEqual(position.volume_long_his, 0)
        self.assertEqual(position.volume_long, 5)
        self.assertEqual(position.volume_long_frozen_today, 0)
        self.assertEqual(position.volume_long_frozen_his, 0)
        self.assertEqual(position.volume_long_frozen, 0)
        self.assertEqual(position.volume_short_today, 6)
        self.assertEqual(position.volume_short_his, 0)
        self.assertEqual(position.volume_short, 6)
        self.assertEqual(position.volume_short_frozen_today, 0)
        self.assertEqual(position.volume_short_frozen_his, 0)
        self.assertEqual(position.volume_short_frozen, 0)
        self.assertEqual(position.open_price_long, 160.0)
        self.assertEqual(position.open_price_short, 117.5)
        self.assertEqual(position.open_cost_long, 8000.0)
        self.assertEqual(position.open_cost_short, 7050.0)
        self.assertEqual(position.position_price_long, 160.0)
        self.assertEqual(position.position_price_short, 117.5)
        self.assertEqual(position.position_cost_long, 8000.0)
        self.assertEqual(position.position_cost_short, 7050.0)
        self.assertEqual(position.float_profit_long, -100.0)
        self.assertEqual(position.float_profit_short, -2430.0)
        self.assertEqual(position.float_profit, -2530.0)
        self.assertEqual(position.position_profit_long, 0.0)
        self.assertEqual(position.position_profit_short, 0.0)
        self.assertEqual(position.position_profit, 0.0)
        self.assertEqual(position.margin_long, 0.0)
        self.assertEqual(position.margin_short, 12996.800000000001)
        self.assertEqual(position.margin, 12996.800000000001)
        self.assertEqual(position.market_value_long, 7900.0)
        self.assertEqual(position.market_value_short, -9480.0)
        self.assertEqual(position.market_value, -1580.0)
        self.assertEqual(position.last_price, 158.0)

        # 其他取值方式测试
        self.assertEqual(position["pos_long_today"], 5)
        self.assertEqual(position["pos_short_today"], 6)
        self.assertEqual(position["volume_long_his"], 0)
        self.assertEqual(position["volume_long"], 5)
        api.close()

    def test_get_trade_option(self):
        """
            获取成交记录
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.mock.run(os.path.join(dir_path, "log_file", "test_td_basic_get_trade_simulate_option.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _td_url=self.td_url, _md_url=self.md_url)
        order1 = api.insert_order("CZCE.SR101C5200", "SELL", "OPEN", 1, limit_price=70)
        order2 = api.insert_order("DCE.m2101-P-2900", "BUY", "OPEN", 2, limit_price=160)

        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()

        trade1 = api.get_trade("PYSDK_insert_8ca5996666ceab360512bd1311072231|1")
        trade2 = api.get_trade("PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2")
        self.assertAlmostEqual(1596766431358968000 / 1e9, trade1.trade_date_time / 1e9, places=1)
        self.assertAlmostEqual(1596766431359799000 / 1e9, trade2.trade_date_time / 1e9, places=1)
        del trade1["trade_date_time"]
        del trade2["trade_date_time"]
        print(str(trade1))
        print(str(trade2))
        self.assertEqual(str(trade1),
                         "{'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_trade_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231|1', 'exchange_id': 'CZCE', 'instrument_id': 'SR101C5200', 'direction': 'SELL', 'offset': 'OPEN', 'price': 70.0, 'volume': 1, 'user_id': 'TQSIM', 'commission': 10}")
        self.assertEqual(str(trade2),
                         "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'DCE', 'instrument_id': 'm2101-P-2900', 'direction': 'BUY', 'offset': 'OPEN', 'price': 160.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 20}")
        self.assertEqual(trade1.direction, "SELL")
        self.assertEqual(trade1.offset, "OPEN")
        self.assertEqual(trade1.price, 70.0)
        self.assertEqual(trade1.volume, 1)
        self.assertEqual(trade1.commission, 10)

        self.assertEqual(trade2.direction, "BUY")
        self.assertEqual(trade2.offset, "OPEN")
        self.assertEqual(trade2.price, 160.0)
        self.assertEqual(trade2.volume, 2)
        self.assertEqual(trade2.commission, 20)
        api.close()
