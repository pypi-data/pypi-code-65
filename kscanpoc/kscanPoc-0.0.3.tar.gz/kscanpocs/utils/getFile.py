# coding: utf-8
# @Time    : 2020/9/16 15:37
# @Author    : WANSUIYE
# @File    : getFile.py
# @Project: kscan_pocs

import os

def get_file_items(filename,commentPrefix='#'):
	retVal = set()

	with open(filename,'r') as f:
		for line in f.readlines():
			if commentPrefix:
				if line.find(commentPrefix) != -1:
					line = line[:line.find(commentPrefix)]
			line = line.strip()
			if line:
				retVal.add(line)

	return retVal

def get_var_items(filename,commentPrefix='#'):
	basepath = os.path.abspath(__file__)
	folder = os.path.dirname(basepath)
	fd=os.path.abspath(os.path.join(folder, "../var/{}".format(filename)))
	return get_file_items(fd,commentPrefix)

def genUserPasswd(userList,passwdList):
	for u in userList:
		for p in passwdList:
			yield u,p