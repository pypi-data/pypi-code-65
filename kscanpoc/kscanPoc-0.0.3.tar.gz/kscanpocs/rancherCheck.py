# coding: utf-8
# @Time    : 2020/9/21 7:56
# @Author    : WANSUIYE
# @File    : rancherCheck.py
# @Project: kscan_pocs

import requests

from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	if flag==1:
		user_list=['admin']
		passwd_list=['pass']
	else:
		user_list = get_var_items('ssh_user.txt')
		user_list.add('admin')
		passwd_list = get_var_items('top200passwd.txt')
		passwd_list.add('pass')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/v3-public/localProviders/local?action=login'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		data = {'username': user, 'password': passwd}
		res = requests.post(url,json = data,verify = False,timeout=timeout)
		if res.status_code!=401 and 'authProvider' in res.text:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Rancher','status':1,'url':''}

	url = '{}://{}:{}'.format(target[0], target[1], int(target[2]))
	res = requests.get(url,verify = False,timeout=timeout)
	if 'login' not in res.text and res.headers.get('X-Rancher-Version'):
		retVal['status'] = 2
		retVal['vul'] = 'unauthorized'
	else:
		for user, passwd in get_dict(flag):
			res = bf(target,user,passwd,timeout)
			if res:
				retVal['status'] = 2
				retVal['url'] += res+'\n'

	return retVal
