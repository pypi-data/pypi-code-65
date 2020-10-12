#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:CHENYANG7
@file:SshPasswdCheck.py
@time:2020/09/29
"""
import subprocess
from math import ceil

import urllib3


def getAuthMethods(target, port=22, timeout=5.0):
    try:
        success_output = subprocess.check_output(
            [
                'ssh',
                '-o', 'StrictHostKeyChecking=no',  # prevents ominous error on changed host key
                '-o', 'PreferredAuthentications=none',  # the point - prevents attempted authentication
                '-o', 'LogLevel=ERROR',  # prevents warning associated with unrecognized host key
                '-o', 'ConnectTimeout=%d' % ceil(timeout),  # maximum time per connections
                '-p', str(port),
                      'root@' + target,  # use root user to prevent leaking username
                'exit'  # the command to be executed upon successful auth
            ],
            stderr=subprocess.STDOUT
        )

        # If we make it here, the server allowed us shell access without authentication.
        # Thankfully, the 'exit' command should have left immediately.
        # logger.info("No authentication")
        return 'NoAuth'

    # This is in fact the expected case, as we expect the SSH server to reject the unauthenticated connection,
    # and therefore expect exit code 255, OpenSSH's sole error code.
    except subprocess.CalledProcessError as e:
        # ssh's result to stderr
        result = str(e.output.strip())

        if e.returncode != 255:
            # logger.info("No authentication")
            return 'NoAuth'
        elif result.startswith('Permission denied (') and result.endswith(').'):
            authMethods = result[19:-2].split(
                ',')  # assume the format specified in the above condition with comma-delimited auth methods
            # logger.info("Authentication methods: %s" % str(authMethods))
            return authMethods
        else:  # re-raise other exceptions, which are various connection errors
            # logger.info("Unexpected case: result=%s" % str(result))
            raise Exception(result)  # we leave subprocess.TimeoutExpired uncaught, so it will propagate


def check(target, **kwargs):
    timeout = kwargs.get('timeout') or 3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    retVal = {'service': 'sshpasswd', 'status': 1, 'url': ''}
    try:
        authMethods = getAuthMethods(target[1], target[2], timeout=timeout)
        if "password" in authMethods:
            retVal['url'] = 'PasswdAuthSSH'
            retVal['status'] = 2
        elif authMethods == 'NoAuth':
            retVal['url'] = 'NoAuthSSH'
            retVal['status'] = 2
        else:
            pass
            # logger.info("Not vuln")
    except Exception as e:
        pass
        # logger.debug("check Password Auth failed, reason:%s" % str(e))
    return retVal
