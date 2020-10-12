#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:ShipyardCheck.py
@time:2020/09/28
"""
import json

import requests
import re
from .utils.getFile import get_var_items, genUserPasswd


def get_dict(flag=1):
    if flag == 1:
        user_list = ['admin']
        passwd_list = ['shipyard']
    else:
        user_list = get_var_items('ssh_user.txt')
        user_list.add('admin')
        passwd_list = get_var_items('top200passwd.txt')
        passwd_list.add('shipyard')
    return genUserPasswd(user_list, passwd_list)


def bf(target, user, passwd, timeout):
    retVal = ''
    debugMsg = "try crack with username:%s password:%s" % (user, passwd)
    # logger.debug(debugMsg)
    try:
        url = '{}://{}:{}/auth/login'.format(target[0], target[1], int(target[2]))
        headers = {"Accept": r"application/json, text/plain, */*",
                   "Content-Type": r"application/json;charset=UTF-8"}
        data = {"username": user, "password": passwd}
        res = requests.post(url, data=json.dumps(data), headers=headers, verify=False, timeout=timeout)

        if res.status_code == 200 and 'auth_token' in res.text:
            infoMsg = "shipyard login success! username:%s  password:%s" % (user, passwd)
            # logger.info(infoMsg)
            retVal = '{}/{}'.format(user, passwd)
    except Exception as e:
        pass
    return retVal


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'Shipyard', 'status': 1, 'url': ''}

    for user, passwd in get_dict(flag):
        res = bf(target, user, passwd, timeout)
        if res:
            retVal['status'] = 2
            retVal['url'] += res + '\n'
    return retVal
