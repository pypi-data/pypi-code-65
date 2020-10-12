# coding: utf-8
#  @Time    : 2020/9/21 6:11
#  @Author    : WANSUIYE
#  @File    : sshCheck.py
#  @Project: kscan_pocs
import paramiko

from .utils.getFile import get_var_items, genUserPasswd
import redis


def get_dict(flag=1):
    user_list = get_var_items('ssh_user.txt')
    passwd_list = get_var_items('ssh_passwd.txt')

    return genUserPasswd(user_list, passwd_list)


def sshCrack(target, port, user, passwd, timeout):
    """
    SSH Crack
    """
    retVal = {}
    try:

        # debugMsg = "try crack with username:%s password:%s" %(user,passwd)
        # logger.debug(debugMsg)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(target, port=port, username=user, password=passwd, timeout=timeout)
        infoMsg = "SSH login success! username:%s  password:%s" % (user, passwd)
        retVal['UserName'] = user
        retVal['Password'] = passwd
        retVal['Type'] = 'BruteForce'


    except Exception as e:
        pass

    return retVal


def bf(target, user, passwd, timeout):
    retVal = ''
    # debugMsg = "try crack with username:%s password:%s" %(user,passwd)
    # logger.debug(debugMsg)
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(target[1], port=target[2], username=user, password=passwd, timeout=timeout)
        infoMsg = "SSH login success! username:%s  password:%s" % (user, passwd)
        retVal = '{}/{}'.format(user, passwd)
    except Exception as e:
        pass
    return retVal


def check(target, **kwargs):
    retVal = {'service': 'redis', 'status': 1, 'url': ''}
    timeout = kwargs.get('timeout') or 3
    flag = kwargs.get('flag') or 1

    for passwd in get_dict(flag):
        res = bf(target, passwd, timeout)
        if res:
            retVal['status'] = 2
            retVal['url'] += res + '\n'

    return retVal
