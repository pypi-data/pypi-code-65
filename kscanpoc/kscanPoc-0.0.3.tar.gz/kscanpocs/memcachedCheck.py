# coding: utf-8
# @Time    : 2020/9/21 5:24
# @Author    : WANSUIYE
# @File    : memcachedCheck.py
# @Project: kscan_pocs

import socket

def check(target,**kwargs):
	retVal = {'service': 'memcached', 'status': 1}
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((target[1], int(target[2])))
		s.send(b'stats\r\n')
		if b'version' in s.recv(1024):
			retVal['status'] = 2
		s.close()
	except Exception as e:
		pass

	return retVal
