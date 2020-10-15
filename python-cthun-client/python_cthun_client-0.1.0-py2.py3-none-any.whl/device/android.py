# -*- coding: utf-8 -*-
__author__ = 'jasonxu'

import os
import subprocess
from cthun_client.common import download_file
from cthun_client.device.device_base import Device

BASE_PATH = "/data/local/tmp"
ANDROID_SCREENSHOT_DIR = "cthun/android_screenshot"
MNC_HOME = "{}/minicap".format(BASE_PATH)
MNC_SO_HOME = "{}/minicap.so".format(BASE_PATH)
MNC_PREBUILT_URL = "https://github.com/Jason916/stf-binaries/raw/master/node_modules/minicap-prebuilt/prebuilt"


def is_device_connected(device_id):
    try:
        subprocess.check_output(["adb", "-s", device_id, "shell", "getprop", "ro.product.model"])
    except subprocess.CalledProcessError:
        return False
    return True


class MinicapInstaller:
    def __init__(self, device_id):
        assert is_device_connected(device_id)
        self.device_id = device_id
        self.abi = self.get_abi()
        self.sdk_version = self.get_sdk_version()
        if self.is_mnc_installed():
            pass
        else:
            self.download_target_mnc()
            self.download_target_mnc_so()

    def get_abi(self):
        abi = subprocess.getoutput("adb -s {} shell getprop ro.product.cpu.abi".format(self.device_id))
        return abi

    def get_sdk_version(self):
        sdk_version = subprocess.getoutput("adb -s {} shell getprop ro.build.version.sdk".format(self.device_id))
        return sdk_version

    def is_installed(self, name):
        return bool(subprocess.check_output([
            "adb", "-s", self.device_id, "shell",
            "find", BASE_PATH, "-name", name])
        )

    def is_mnc_installed(self):
        return self.is_installed("minicap") and self.is_installed("minicap.so")

    def download_target_mnc(self):
        target_minicap_url = "{}/{}/bin/minicap".format(MNC_PREBUILT_URL, self.abi)
        mnc_path = download_file(target_minicap_url)
        subprocess.check_call(["adb", "-s", self.device_id, "push", mnc_path, MNC_HOME], stdout=subprocess.DEVNULL)
        subprocess.check_call(["adb", "-s", self.device_id, "shell", "chmod", "777", MNC_HOME])
        os.remove(mnc_path)

    def download_target_mnc_so(self):
        target_url = "{}/{}/lib/android-{}/minicap.so".format(MNC_PREBUILT_URL, self.abi, self.sdk_version)
        mnc_so_path = download_file(target_url)
        subprocess.check_call(["adb", "-s", self.device_id, "push", mnc_so_path, MNC_SO_HOME],
                              stdout=subprocess.DEVNULL)
        subprocess.check_call(["adb", "-s", self.device_id, "shell", "chmod", "777", MNC_SO_HOME])
        os.remove(mnc_so_path)


class Android(Device):

    def __init__(self, device_id):
        self.device_id = device_id
        MinicapInstaller(device_id)

    def get_device_screen_size(self):
        result_str = subprocess.check_output(["adb", '-s', self.device_id, 'shell', 'wm', 'size']).decode("utf-8")
        width, height = result_str.replace('\n', '').replace('\r', '').split(' ')[-1].split('x')
        return width, height

    def take_screenshot(self):
        if not os.path.exists(ANDROID_SCREENSHOT_DIR):
            os.makedirs(ANDROID_SCREENSHOT_DIR)
        screen = self.get_device_screen_size()
        screen_size = '{}x{}@{}x{}/0'.format(screen[0], screen[1], screen[0], screen[1])
        subprocess.check_call([
            "adb", "-s", self.device_id, "shell",
            "LD_LIBRARY_PATH={}".format(BASE_PATH), MNC_HOME, "-s", "-P", screen_size,
            ">", "{}/temp.jpg".format(BASE_PATH)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def pull_screenshot(self, target_path):
        subprocess.check_call([
            "adb", "-s", self.device_id,
            'pull', "{}/temp.jpg".format(BASE_PATH), f"{target_path}/temp.jpg"
        ], stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    pass
