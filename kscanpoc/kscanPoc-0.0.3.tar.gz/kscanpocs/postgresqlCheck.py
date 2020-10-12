# coding: utf-8
# @Time    : 2020/9/21 5:57
# @Author    : WANSUIYE
# @File    : postgresqlCheck.py
# @Project: kscan_pocs

from .utils.getFile import get_var_items,genUserPasswd
import psycopg2

def get_dict(flag=1):
	user_list = get_var_items('ssh_user.txt')
	passwd_list = get_var_items('top200passwd.txt')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	retVal=''
	try:
		psycopg2.connect(host=target[1], port=int(target[2]), user=user, password=passwd)
		retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	retVal={'service':'postgresql','status':1,'url':''}
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal