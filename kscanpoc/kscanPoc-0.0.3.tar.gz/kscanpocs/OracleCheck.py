#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:OracleCheck.py
@time:2020/09/29
"""
import requests
from .utils.getFile import get_var_items, genUserPasswd
import cx_Oracle


def get_dict(flag=1):
    if flag == 1:
        user_list = ['sys', 'system', 'sysman', 'scott', 'aqadm', 'Dbsnmp']
        passwd_list = ['', 'manager', 'oem_temp', 'tiger', 'aqadm', 'dbsnmp']
    else:
        user_list = get_var_items('mongodb_user.txt')
        for i in ['sys', 'system', 'sysman', 'scott', 'aqadm', 'Dbsnmp']:
            user_list.add(i)
        passwd_list = get_var_items('mongodb_passwd.txt')
        for p in ['', 'manager', 'oem_temp', 'tiger', 'aqadm', 'dbsnmp']:
            passwd_list.add(p)
    return genUserPasswd(user_list, passwd_list)


def bf(target, user, passwd,timeout):

    retVal = ''
    try:
        cx_Oracle.connect(user, passwd, '{}:{}/{}'.format(target[1], target[2], 'orcl'))  # oracle默认server名为orcl

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
