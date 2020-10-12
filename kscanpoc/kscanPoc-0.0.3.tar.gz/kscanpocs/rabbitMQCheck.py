# coding: utf-8
# @Time    : 2020/9/15 17:55
# @Author    : WANSUIYE
# @File    : rabbitMQCheck.py
# @Project: poc
import requests
from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):
	if flag==1:
		user_list=['guest']
		passwd_list=['guest']
	else:
		user_list = get_var_items('ssh_user.txt')
		user_list.add('guest')
		passwd_list = get_var_items('top200passwd.txt')
		passwd_list.add('guest')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	url = '{}://{}:{}/api/whoami'.format(target[0], target[1], int(target[2]))
	retVal=''
	try:
		res = requests.get(url, auth=(user, passwd), verify=False, timeout=timeout)
		if res.status_code == 200:
			retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'RabbitMQ Management','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal