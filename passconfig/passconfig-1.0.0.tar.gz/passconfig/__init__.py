#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    A Simple Username and Password Manager
"""
import os
import json

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import click
from simple_loggers import SimpleLogger


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_DEFAULT = os.path.join(os.path.expanduser('~'), '.passconfig.ini')

version_info = json.load(open(os.path.join(BASE_DIR, 'version.json')))


class PassConfig(object):
    """
    >>> from passconfig import PassConfig
    >>> pc = PassConfig()
    >>> username, password = pc.get()
    >>> if True:
    >>>     pc.save()
    """
    logger = SimpleLogger('PassConfig')
    def __init__(self, username=None, password=None, configfile=CONFIG_DEFAULT, section='common'):
        self.username = username
        self.password = password
        self.configfile = configfile
        self.section = section

        self.conf = ConfigParser()
        if configfile:
            self.conf.read(configfile)

    def get(self):
        """
            Return usernane, password
        """
        if self.username and self.password:
            username, password = self.username, self.password
        elif os.path.exists(self.configfile):
            username, password = self.read()
        else:
            username, password = None, None

        if not all([username, password]):
            click.secho('please input your username and password', fg='yellow')
            username = username or click.prompt('>>> username')
            password = click.prompt('>>> password', hide_input=True, confirmation_prompt=True)
        
        self.username = username
        self.password = password
        return username, password

    def read(self):
        """
            Read username and password from configfile
        """
        password = None
        username = self.username

        if not self.conf.has_section(self.section):
            pass
        elif username and self.conf.has_option(self.section, self.username):
            password = self.conf.get(self.section, self.username)
        elif not self.username and len(self.conf.options(self.section)) == 1:
            username = self.conf.options(self.section)[0]
            password = self.conf.get(self.section, username)

        return username, password

    @staticmethod
    def safe_open(filename, mode='r'):
        """
            Make directory firstly if not exists
        """
        if 'w' in mode:
            dirname = os.path.dirname(filename)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname)
        return open(filename, mode)

    def save(self):
        """
            Save username and password to configfile
        """
        if not self.conf.has_section(self.section):
            self.conf.add_section(self.section)
        self.conf.set(self.section, self.username, self.password)

        with self.safe_open(self.configfile, 'w') as out:
            self.conf.write(out)
            self.logger.info('save username and password to file: {}'.format(self.configfile))


if __name__ == '__main__':
    pc = PassConfig(configfile='test.ini', username='suqingdong')
    username, password = pc.get()
    print(username, password)

    # login of something, save if right
    if True:
        pc.save()
