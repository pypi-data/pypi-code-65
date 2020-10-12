#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:RsyncCheck.py
@time:2020/09/29
"""

import requests
import urllib3
from lib.core.nmapwrapper import Nmap


def check(target, **kwargs):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    retVal = {'service': 'rsync', 'status': 1, 'url': ''}
    script_id = 'rsync-brute'
    nmap = Nmap('{}:{}:rsync'.format(target[1], target[2]), str(target[2]))
    nmap.host_services_cmd += ' --script %s' % script_id
    scan_res = nmap.get_host_services(target[1])

    try:
        nmap.clean_file()
    except Exception as e:
        print('clean nmap temp xml file failed: %s' % e)

    if scan_res:
        if len(scan_res) == 1:
            for key, value in scan_res.items():
                for port, service, banner, version, script in value:
                    if script:
                        rsync = script[0][script_id].split('\n')
                        retVal['url'] = rsync
                        retVal['status'] = 2
    return retVal
