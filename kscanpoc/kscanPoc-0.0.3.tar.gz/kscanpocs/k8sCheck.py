# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：kscan_pocs -> k8sCheck
@IDE    ：PyCharm
@Author ：wansuiye
@Date   ：2020/9/25 7:06
@Desc   ：
=================================================='''

import requests


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'Kubernetes', 'status': 1}
    url = '{}://{}:{}'.format(target[0], target[1], int(target[2]))
    try:
        res = requests.get(url, verify=False, timeout=timeout)
        common_uri = '/api/v1/nodes'
        metrics = '/metrics'
        paths = res.json()['paths']
        if requests.get(url + common_uri, verify=False, timeout=timeout).status_code == 200:
            retVal['vul'] = 'unauthorized'
            retVal['url'] = url + common_uri
            retVal['status'] = 2
        elif metrics in paths:
            if requests.get(url + metrics, verify=False, timeout=timeout).status_code == 200:
                retVal['Type'] = 'Information disclosure'
                retVal['url'] = url + metrics
                retVal['status'] = 2
    except:
        pass

    return retVal

