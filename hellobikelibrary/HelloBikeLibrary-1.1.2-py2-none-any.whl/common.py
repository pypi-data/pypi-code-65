# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-03-10 14:52:05
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2020-08-21 15:50:31

from robot.api import logger
from HelloBikeLibrary.request import Request
import json

__version__ = "1.0"

class Common(object):

	def __sendCodeV3(self,mobilePhone,env="uat"):
		if env == "uat":
			url = "https://uat-api.hellobike.com/api"
		else:
			url = "https://fat-api.hellobike.com/api"
		data = {
			"mobile" : mobilePhone,
			"source" : 0,
			"riskControlData" : {
			"userAgent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
			"deviceLon" : "121.363833",
			"roam" : "460",
			"systemCode" : "61",
			"deviceLat" : "31.122775"
			},
			"action" : "user.account.sendCodeV3"
		}
		rep = Request().request_client(url=url,data=data)

	def login_auth_app(self,mobilePhone,env="uat"):
		"""
			app登陆认证
			mobilePhone 登陆手机号
			env 不传默认为uat
			返回token,guid
		"""
		self.__sendCodeV3(mobilePhone,env)
		if env == "uat":
			app_url = "https://uat-api.hellobike.com/auth"
		else:
			app_url = "https://fat-api.hellobike.com/auth"
		data = {
		"clientId" : "01L01610000038690879",
		"version" : "5.34.0",
		"riskControlData" : {
			"userAgent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
			"deviceLon" : "121.363761",
			"roam" : "460",
			"systemCode" : "61",
			"deviceLat" : "31.122788"
		},
		"mobile" : mobilePhone,
		"longitude" : "121.363800",
		"latitude" : "31.122782",
		"cityCode" : "021",
		"code" : "1234",
		"action" : "user.account.login",
		"city" : "上海市",
		"systemCode" : "61",
		"adCode" : "310112"
		}
		rep = Request().request_client(url=app_url,data=data)
		print(rep)
		if rep[0] == 200:
			content = rep[1]
			if content.get('data').get('token'):
				logger.info(content.get('data'))
				return content.get('data').get('token'),content.get('data').get('guid')
		else:
			raise Exception("App登陆失败")

if __name__ == '__main__':
	com = Common()
	print(com.login_auth_app("12010002002",env="uat"))
	# print(com.login_auth_app("12010060001",env="uat"))

