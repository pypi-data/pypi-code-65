#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:EsUnauthCheck.py
@time:2020/09/28
"""

import requests
import urllib3


def check(target, **kwargs):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'elasticsearch', 'status': 1}
    url = '{}://{}/_cat:{}'.format(target[0], target[1], int(target[2]))
    requests.packages.urllib3.disable_warnings()
    try:
        res = requests.get(url, verify=False, timeout=timeout)
        if '/_cat/master' in '{}'.format(res.text):
            retVal['url'] = url
            retVal['status'] = 2
    except:
        pass

    return retVal
