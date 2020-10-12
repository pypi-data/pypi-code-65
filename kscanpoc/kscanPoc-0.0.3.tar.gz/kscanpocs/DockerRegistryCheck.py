# coding: utf-8
# @Time    : 2020/9/16 14:17
# @Author    : WANSUIYE
# @File    : DockerRegistryCheck.py
# @Project: kscan_pocs

import requests
def check(target,**kwargs):
	timeout = kwargs.get('timeout') or 3
	flag = kwargs.get('flag') or 1
	retVal={'service':'Docker Registry','status':1}
	url = '{}://{}:{}/v2/_catalog'.format(target[0], target[1], int(target[2]))
	try:
		res = requests.get(url, verify=False, timeout=timeout)
		if 'repositories' in res.text:
			retVal['url'] = url
			retVal['status'] = 2
	except:
		pass

	return retVal
