#    _________             .__
#   /   _____/____    _____|  |__ _____
#   \_____  \\__  \  /  ___/  |  \\__  \
#   /        \/ __ \_\___ \|   Y  \/ __ \_
#  /_______  (____  /____  >___|  (____  /
#          \/     \/     \/     \/     \/
#    _________       _____  __
#   /   _____/ _____/ ____\/  |_
#   \_____  \ /  _ \   __\\   __\
#   /        (  <_> )  |   |  |
#  /_______  /\____/|__|   |__|
#          \/
#  Copyright (c) 2020.

"""
user class with save and load function
"""

import os
import re
from datetime import datetime

from login_gui.user import User


class Loader:
    """loader class can load file to read and write user class data"""
    __path = str
    __is_exist = bool
    __last_date = str

    def __init__(self, path=None):
        self.path = path
        self.read()

    @property
    def path(self):
        """path of file"""
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value
        if value is None:
            self.__path = os.path.abspath(os.getenv('APPDATA') + '\\.JiraApiAS\\Login')
            return

    @property
    def last_date(self):
        """get last date of save file with user data"""
        return self.__last_date

    @last_date.setter
    def last_date(self, value):
        if not isinstance(value, str):
            raise TypeError('value must be bool!')  # pragma: no cover
        self.__last_date = value

    @property
    def is_exist(self):
        """state if exist file"""
        return self.__is_exist

    @is_exist.setter
    def is_exist(self, value):
        if not isinstance(value, bool):
            raise TypeError('value must be bool!')  # pragma: no cover
        self.__is_exist = value

    def read(self):
        """read user class data from file"""
        self.is_exist = False
        self.last_date = ''
        if os.path.exists(self.path):  # pragma: no cover
            file = open(self.path, 'r')
            line = file.readline()
            if line != '':  # pragma: no cover
                split_line = re.findall(r'.(\d+.\d+.\d+).', line)
                self.last_date = split_line[0]
                User().save(line.replace('[' + self.last_date + ']', '').encode('ascii'))
                self.is_exist = True
            file.close()

    def write(self, value):  # pragma: no cover
        """write user class data to file"""
        dir_name = os.path.dirname(self.path)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        file = open(self.path, 'w')
        today = datetime.now().strftime("[%d.%m.%Y]")
        file.write(today + value.decode())
        file.close()
