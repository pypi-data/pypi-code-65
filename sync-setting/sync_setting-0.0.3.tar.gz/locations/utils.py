import sys
from enum import Enum
import os


class Platform(Enum):
    windows = 0
    linux = 1
    mac = 2
    unknown = 3


platform = None
home = os.path.expanduser('~')

def _init_platform():
    global platform, home
    if sys.platform.startswith('win'):
        platform = Platform.windows
    elif sys.platform.startswith('linux'):
        platform = Platform.linux
        if os.path.exists('/mnt/c'):
            username = input("please input your username: ")
            home = "/mnt/c/Users/%s" % username
            platform = Platform.windows
    elif sys.platform.startswith('darwin'):
        platform = Platform.mac
    else:
        platform = Platform.unknown


_init_platform()
