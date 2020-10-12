# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：kscan_pocs -> yarnCheck
@IDE    ：PyCharm
@Author ：wansuiye
@Date   ：2020/9/25 8:11
@Desc   ：
=================================================='''

import requests


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'hadoop_yarn', 'status': 1}
    url = '{}://{}:{}/ws/v1/cluster/apps/new-application'.format(target[0], target[1], int(target[2]))
    try:
        res = requests.post(url, verify=False, timeout=timeout)
        if 'application-id' in res.text:
            retVal['url'] = url
            retVal['status'] = 2
    except:
        pass

    return retVal
