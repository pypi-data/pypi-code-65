# !usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yanqiong'

import json
import os

import jwt
import requests

import tqsdk


class TqAuth(object):
    """信易用户认证类"""

    def __init__(self, user_name: str = "", password: str = ""):
        """
        创建信易用户认证类

        Args:
            user_name (str): [必填]信易账户，可以是 邮箱、用户名、手机号

            password (str): [必填]信易账户密码


        Example::

            # 使用实盘帐号直连行情和交易服务器
            from tqsdk import TqApi, TqAccount, TqAuth
            api = TqApi(TqAccount("H海通期货", "022631", "123456"), auth=TqAuth("信易账户", "账户密码"))

            # 等价于
            # api = TqApi(TqAccount("H海通期货", "022631", "123456"), auth="信易账户", "账户密码")
        """
        self._user_name = user_name
        self._password = password
        self._auth_url = os.getenv("TQ_AUTH_URL", "https://auth.shinnytech.com")
        self._access_token = ""
        self._refresh_token = ""
        self._auth_id = ""
        self._grants = {
            "features": [],
            "accounts": []
        }

    @property
    def _base_headers(self):
        return {
            "User-Agent": "tqsdk-python %s" % tqsdk.__version__,
            "Accept": "application/json",
            "Authorization": "Bearer %s" % self._access_token
        }

    def login(self):
        self._access_token, self._refresh_token = self._request_token({
            "grant_type": "password",
            "username": self._user_name,
            "password": self._password
        })
        content = jwt.decode(self._access_token, verify=False)
        self._grants = content["grants"]
        self._auth_id = content["sub"]

    def _request_token(self, payload):
        data = {"client_id": "shinny_tq", "client_secret": "be30b9f4-6862-488a-99ad-21bde0400081"}
        data.update(payload)
        response = requests.post(url=f"{self._auth_url}/auth/realms/shinnytech/protocol/openid-connect/token",
                                 headers=self._base_headers, data=data, timeout=30)
        if response.status_code == 200:
            content = json.loads(response.content)
            return content["access_token"], content["refresh_token"]
        else:
            raise Exception("用户权限认证失败 (%d,%s)" % (response.status_code, json.loads(response.content)))

    def _add_account(self, account_id):
        if self._has_account(account_id):
            return True
        response = requests.put(
            url=f"{self._auth_url}/auth/realms/shinnytech/rest/update-grant-accounts/{account_id}",
            headers=self._base_headers,
            timeout=30)
        if response.status_code == 200:
            self._access_token, self._refresh_token = self._request_token({
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            })
            content = jwt.decode(self._access_token, verify=False)
            self._grants.update(content["grants"])
        else:
            raise Exception(f"添加期货账户失败。{response.status_code}, {json.loads(response.content)}")

    def _get_td_url(self, broker_id, account_id):
        """获取交易网关地址"""
        response = requests.get(
            url=f"https://files.shinnytech.com/{broker_id}.json",
            params={
                "account_id": account_id,
                "auth": self._user_name
            },
            headers=self._base_headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"不支持该期货公司 - {broker_id}，请联系期货公司。")
        broker_list = json.loads(response.content)
        if "TQ" not in broker_list[broker_id]["category"]:
            raise Exception(f"该期货公司 - {broker_id} 暂不支持 TqSdk 登录，请联系期货公司。")
        return broker_list[broker_id]["url"]

    def _get_md_url(self, stock):
        """获取行情网关地址"""
        response = requests.get(
            url="https://api.shinnytech.com/ns",
            headers=self._base_headers,
            params={"stock": str(stock).lower()},
            timeout=30
        )
        if response.status_code == 200:
            content = json.loads(response.content)
            if "mdurl" in content:
                return content["mdurl"]
            else:
                raise Exception(f"调用名称服务失败: {content}")
        else:
            raise Exception(f"调用名称服务失败: {response.status_code}, {response.content}")

    def _has_feature(self, feature):
        return feature in self._grants["features"]

    def _has_account(self, account):
        return account in self._grants["accounts"]

    def _has_md_grants(self, symbol):
        if symbol.split('.', 1)[0] in ["SHFE", "DCE", "CZCE", "INE", "CFFEX", "KQ", "SSWE"] and self._has_feature("futr"):
            return True
        if symbol.split('.', 1)[0] in ["SSE", "SZSE"] and self._has_feature("sec"):
            return True
        if symbol in ["SSE.000016", "SSE.000300", "SSE.000905"] and self._has_feature("lmt_idx"):
            return True
        raise Exception(f"您的账户不支持查看 {symbol} 的行情数据，需要购买专业版本后使用。升级网址：https://account.shinnytech.com")

    def _has_td_grants(self, symbol):
        # 对于 opt / cmb / adv 权限的检查由 OTG 做
        if symbol.split('.', 1)[0] in ["SSE", "SZSE"] and self._has_feature("sec"):
            return True
        if symbol.split('.', 1)[0] in ["SHFE", "DCE", "CZCE", "INE", "CFFEX", "KQ"] and self._has_feature("futr"):
            return True
        raise Exception(f"您的账户不支持交易 {symbol}，需要购买专业版本后使用。升级网址：https://account.shinnytech.com")
