# -*- encoding: utf-8 -*-
# @ModuleName: Db_Reader
# @Function: 	read_tdx_1min_data 获取分钟数据
# 				read_ts_top_inst 获取龙虎榜机构明细
# 				read_ts_top_list 获取龙虎榜股票明细
# 				read_ts_day_data 获取日线综合数据
# 				read_ts_index_daily 获取指数日线数据
# 				read_ts_limit_list 获取每日涨停板数据
# 				read_ts_moneyflow_hsgt 获取沪深港通资金流数据
# 				read_concept_data 获取板块信息
# @Author: Yulin Qiu
# @Time: 2020-3-6 20:08:00


import sqlite3
import pandas as pd
import datetime
import os
import tushare as ts
import numpy as np
from pathlib import Path

class FutureReader:
	def __init__(self, *args, **kwargs):
		self.dbpath = None
		configpath = Path.home().joinpath('.qytools')
		if os.path.exists(str(configpath.joinpath('dbname_config.json'))):
			df_config = pd.read_json(str(configpath.joinpath('dbname_config.json')))
			self.config = df_config
			self.file_used = df_config.loc[0, 'file_used']
			self.dbpath = df_config.loc[0, 'dbpath']
			self.configpath = str(configpath)
			print('配置文件dbname_config.json读取成功')
		else:
			raise FileNotFoundError('配置文件不存在,请执行DBreader.firsttime_setconfig')

		try:
			pro = ts.pro_api()
		except:
			print('tushare连接出错，使用配置文件中token重新尝试连接')
			try:
				ts.set_token(df_config.loc[0, 'tushare_token'])
				pro = ts.pro_api()
			except:
				raise ConnectionError('使用配置文件中token连接tushare失败，请联系管理员')

		df_opendate = pro.query('trade_cal', start_date='20150101', end_date='20991231')  # 获取交易日
		df_opendate = df_opendate[df_opendate.is_open == 1]['cal_date']
		self.open_date = df_opendate.apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])

		# 目前正常交易股票代码和名称
		# 大商所
		self.dce_ordinary = pro.fut_basic(
			exchange='DCE',
			fut_type='1',
			fields='symbol,fut_code,name,list_date,delist_date'
		)
		self.dce_main = pro.fut_basic(
			exchange='DCE',
			fut_type='2',
			fields='symbol,fut_code,name'
		)

		# 中金所
		self.cffex_ordinary = pro.fut_basic(
			exchange='CFFEX',
			fut_type='1',
			fields='symbol,fut_code,name,list_date,delist_date'
		)
		self.cffex_main = pro.fut_basic(
			exchange='CFFEX',
			fut_type='2',
			fields='symbol,fut_code,name'
		)

		# 郑商所
		self.czce_ordinary = pro.fut_basic(
			exchange='CZCE',
			fut_type='1',
			fields='symbol,fut_code,name,list_date,delist_date'
		)
		self.czce_main = pro.fut_basic(
			exchange='CZCE',
			fut_type='2',
			fields='symbol,fut_code,name'
		)

		# 上期所
		self.shfe_ordinary = pro.fut_basic(
			exchange='SHFE',
			fut_type='1',
			fields='symbol,fut_code,name,list_date,delist_date'
		)
		self.shfe_main = pro.fut_basic(
			exchange='SHFE',
			fut_type='2',
			fields='symbol,fut_code,name'
		)

		# 上海国际能源交易中心
		self.ine_ordinary = pro.fut_basic(
			exchange='INE',
			fut_type='1',
			fields='symbol,fut_code,name,list_date,delist_date'
		)
		self.ine_main = pro.fut_basic(
			exchange='INE',
			fut_type='2',
			fields='symbol,fut_code,name'
		)

		self._date_str_change(self.dce_ordinary)
		self._date_str_change(self.dce_main)

		self._date_str_change(self.cffex_ordinary)
		self._date_str_change(self.cffex_main)

		self._date_str_change(self.czce_ordinary)
		self._date_str_change(self.czce_main)

		self._date_str_change(self.ine_ordinary)
		self._date_str_change(self.ine_main)

		self._date_str_change(self.shfe_ordinary)
		self._date_str_change(self.shfe_main)

	@staticmethod
	def _date_str_change(df):
		df.rename(columns={'symbol': 'code'})
		if 'list_date' in df.columns:
			df['list_date'] = df['list_date'].apply(lambda x: f"{x[0:4]}-{x[4:6]}-{x[6:8]}")
			df['delist_date'] = df['delist_date'].apply(lambda x: f"{x[0:4]}-{x[4:6]}-{x[6:8]}")

	@staticmethod
	def __check_dbtablename(dbname, tablename):
		assert isinstance(dbname, str), 'dbname必须为str，如tushare_data.sqlite3或tushare_data'
		assert isinstance(tablename, str), 'tablename必须为str如ts_day_data'
		if '.sqlite3' in dbname:
			pass
		else:
			dbname = dbname + '.sqlite3'
		return dbname

	# 确定shift和forward时间
	def __check_timechange(self, start, end, shift, forward, minmode=False):
		if not isinstance(shift, int) or not isinstance(forward, int) or shift < 0 or forward < 0:
			raise ValueError('shift必须为大于0的int')
		else:
			if shift == 0:
				str_start = start
				pass
			else:
				str_start = self.open_date[self.open_date < start].tail(shift).tolist()[0]

			if forward == 0:
				str_end = end
				pass
			else:
				if len(self.open_date[self.open_date > end]) > 0:
					str_end = self.open_date[self.open_date > end].head(forward).tolist()[-1]
				else:
					raise ValueError('forward时间过长,不能穿越到未来！')
			if minmode:
				str_start = '{0}{1}{2}{0}'.format('"', str_start, ' 00:00:00')
				str_end = '{0}{1}{2}{0}'.format('"', str_end, ' 23:00:00')
			else:
				str_start = '{0}{1}{0}'.format('"', str_start)
				str_end = '{0}{1}{0}'.format('"', str_end)
			return str_start, str_end

	@staticmethod
	def get_tableinfo_cols(dbfile, tablename):
		df_tableinfo = pd.read_sql('PRAGMA table_info([' + tablename + '])', con=sqlite3.connect(str(dbfile)))
		return df_tableinfo['name'].to_list()

	def check_time(self, time):
		time = pd.to_datetime(time)
		return

	def __check_code(self, code, exchange, fut_type, start, end):
		if code is None:
			pass
		if isinstance(code, list):
			code = '(' + ','.join(map(lambda x: str(int(x)), code)) + ')'
			str_code = 'code in ' + code + ' AND '
		elif isinstance(code, int):
			code = '(' + str(code) + ')'
			str_code = 'code in ' + code + ' AND '
		elif isinstance(code, pd.Series):
			code = '(' + ','.join(map(lambda x: str(int(x)), code.to_list())) + ')'
			str_code = 'code in ' + code + ' AND '
		else:
			raise ValueError('输入的code为{},请保证code格式为 list 或 int'.format(type(code)))

		return str_code

	@staticmethod
	def __check_fields(fields, standard_fields):
		# 全选处理
		if fields == '*':
			return fields
		else:
			# str形式处理
			if isinstance(fields, str):
				try:
					fieldslist = fields.split(',')
					errorlist = []
					for column in fieldslist:
						if column in standard_fields:
							pass
						else:
							errorlist.append(column)
					if len(errorlist) == 0:
						return fields
					else:
						raise ValueError('当前查询表内不存在列名：{}'.format(errorlist))
				except:
					raise ValueError('fields输入有误，非合法字符串或字符串list')
			# list形式处理
			if hasattr(fields, "__iter__"):
				errorlist = []
				for column in fields:
					if column in standard_fields:
						pass
					else:
						errorlist.append(column)
				if len(errorlist) == 0:
					str_fields = ','.join(fields)
					return str_fields
				else:
					raise ValueError('当前查询表内不存在列名：{}'.format(errorlist))

	def query_future_day(
		self, start, end, tablename, dbname, exchange, fut_type, fields='*', code=None):
		dbname = self.__check_dbtablename(dbname, tablename)
		"""
		:param start: 开始日期，必选，支持int(20180808), datetime('2018-08-08 00:00:00'), str('20180808')
		:param end: 结束日期 ，必选，支持同start
		:param tablename: 查询表名，str类型
		:param dbname: 数据库名，str类型，后缀可加可不加，如test或test.sqlite3均合法
		:param exchange: 交易所代码 CFFEX-中金所 DCE-大商所 CZCE-郑商所 SHFE-上期所 INE-上海国际能源交易中心
		:param fut_type: 合约类型 int, 1 普通合约 2主力与连续合约
		:param fields: 要从库中取出的列名,默认取所有，支持str和list[str]，例如'code,high', ['code','high']
		:param code: 代码，默认取所有，支持str如'ZC011', list如['SA011', 'ZC011']

		:return: dataframe格式数据表.
		"""

		col = self.get_tableinfo_cols(
			os.path.join(self.config.loc[0, 'dbpath'], dbname),
			tablename
		)
		start_date = self.check_time(time=start)
		end_date = self.check_time(time=end)
		str_code = self.__check_code(code=code)
		str_fields = self.__check_fields(fields=fields, standard_fields=col)

	def	query_future_min(
			self, start, end, tablename, dbname, fields='*', code=None, shift=0, forward=0,
			time_start=None, time_end=None):
		pass

if __name__ == '__main__':
	f = FutureReader()