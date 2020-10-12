#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:SentinelCheck.py
@time:2020/09/28
"""

import requests
import re
from .utils.getFile import get_var_items, genUserPasswd


def get_dict(flag=1):
    if flag == 1:
        user_list = ['sentinel']
        passwd_list = ['sentinel']
    else:
        user_list = get_var_items('ssh_user.txt')
        user_list.add('sentinel')
        passwd_list = get_var_items('top200passwd.txt')
        passwd_list.add('sentinel')
    return genUserPasswd(user_list, passwd_list)


def bf(target, user, passwd,timeout):
    retVal = ''
    try:
        url = '{}://{}:{}/auth/login?password={}&username={}'.format(target[0], target[1], int(target[2]), passwd, user)
        res = requests.post(url, verify=False,timeout=timeout)

        if res.status_code == 200 and '"success":true' in res.text:
            infoMsg = "sentinel login success! username:%s  password:%s" % (user, passwd)
            # todo   日志记录以上
            retVal = '{}/{}'.format(user, passwd)
    except:
        pass
    return retVal


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'Sentinel', 'status': 1, 'url': ''}

    for user, passwd in get_dict(flag):
        res = bf(target, user, passwd,timeout)
        if res:
            retVal['status'] = 2
            retVal['url'] += res + '\n'
    return retVal
