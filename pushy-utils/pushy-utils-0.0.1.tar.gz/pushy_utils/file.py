import os
import shutil
import winreg


def get_desktop():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, "Desktop")[0]


def get_md5(path):
    files_md5 = os.popen('md5 %s' % path).read().strip()
    file_md5 = files_md5.replace('MD5 (%s) = ' % path, '')
    return file_md5


def copy_dir(src, dst):
    for files in os.listdir(src):
        name = os.path.join(src, files)
        back_name = os.path.join(dst, files)
        if os.path.isfile(name):
            if os.path.isfile(back_name):
                if get_md5(name) != get_md5(back_name):
                    shutil.copy(name, back_name)
            else:
                shutil.copy(name, back_name)
        else:
            if not os.path.isdir(back_name):
                os.makedirs(back_name)
            copy_dir(name, back_name)
