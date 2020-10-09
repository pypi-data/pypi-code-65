import subprocess
import sys
import os


def conan_works(conan_exe):
    try:
        subprocess.check_call([conan_exe, "remote", "list"])
        return True
    except:
        return False


def check_python3():
    if not sys.version_info >= (3,):
        raise RuntimeError("python 3.x strictly required for this script. please install python3 on your platform.")