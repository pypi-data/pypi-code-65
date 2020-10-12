# coding: utf-8
# @Time    : 2020/9/21 6:03
# @Author    : WANSUIYE
# @File    : redisCheck.py
# @Project: kscan_pocs

from .utils.getFile import get_var_items,genUserPasswd
import redis

def get_dict(flag=1):
	passwd_list = get_var_items('top200passwd.txt')

	return passwd_list

def bf(target,passwd,timeout):
	retVal=''
	try:
		if passwd == '':
			r = redis.Redis(host=target[1], port=int(target[2]), db=0, socket_timeout=timeout)
			rs = r.info()
		else:
			r = redis.Redis(host=target[1], port=int(target[2]), db=0, password=passwd, socket_timeout=timeout)
			rs = r.info()
		if rs:
			retVal = passwd
	except:
		pass
	return retVal

def check(target,**kwargs):
	retVal={'service':'redis','status':1,'url':''}
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1

	for passwd in get_dict(flag):
		res = bf(target,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal
