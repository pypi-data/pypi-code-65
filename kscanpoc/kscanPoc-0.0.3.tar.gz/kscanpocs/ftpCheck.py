# coding: utf-8
# @Time    : 2020/9/16 15:32
# @Author    : WANSUIYE
# @File    : ftpCheck.py
# @Project: kscan_pocs

import ftplib
from .utils.getFile import get_var_items,genUserPasswd

def get_dict(flag=1):

	user_list = get_var_items('ftp_user.txt')
	passwd_list = get_var_items('ftp_passwd.txt')

	return genUserPasswd(user_list, passwd_list)

def bf(target,user,passwd,timeout):
	retVal=''
	try:
		ftp = ftplib.FTP(host=target[1], user=user, passwd=passwd, timeout=timeout)
		retVal = '{}/{}'.format(user,passwd)
	except:
		pass
	return retVal

def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'ftp','status':1,'url':''}

	for user, passwd in get_dict(flag):
		res = bf(target,user,passwd,timeout)
		if res:
			retVal['status'] = 2
			retVal['url'] += res+'\n'

	return retVal

