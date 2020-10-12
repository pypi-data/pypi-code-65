# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：kscan_pocs -> swarmCheck
@IDE    ：PyCharm
@Author ：wansuiye
@Date   ：2020/9/25 7:22
@Desc   ：
=================================================='''

import requests


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'docker-swarm', 'status': 1}
    url = '{}://{}:{}/info'.format(target[0], target[1], int(target[2]))
    try:
        res = requests.get(url, verify=False, timeout=timeout)
        if '"Authorization":null' in res.text:
            retVal['url'] = url
            retVal['status'] = 2
    except:
        pass

    return retVal
