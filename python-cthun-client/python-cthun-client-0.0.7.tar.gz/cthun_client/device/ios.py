# -*- coding: utf-8 -*-
__author__ = 'jasonxu'

import os
import subprocess
from cthun_client.common import download_file
from cthun_client.device.device_base import Device

DISKIMAGE_DIR = "cthun/disk_image"
IOS_SCREENSHOT_DIR = "cthun/iOS_screenshot"
IDEVICE_INFO = "/usr/local/bin/ideviceinfo"
IDEVICE_SCREENSHOT = "/usr/local/bin/idevicescreenshot"
iOSDeveloperDiskImageUrl = "https://github.com/Jason916/iOSDeveloperDiskImage/raw/master"


class Ios(Device):

    def __init__(self, device_id):
        self.dependent_check()
        self.device_id = device_id

    @staticmethod
    def dependent_check():
        if not os.path.exists(IOS_SCREENSHOT_DIR):
            os.makedirs(IOS_SCREENSHOT_DIR)
        if not os.path.exists(DISKIMAGE_DIR):
            os.makedirs(DISKIMAGE_DIR)
        # ideviceinfo check
        if not os.path.exists(IDEVICE_INFO):
            return "ideviceinfo command not found, check your libimobiledevice"
        else:
            device_info = subprocess.Popen(IDEVICE_INFO, shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            error_info = device_info.stderr.read().decode()
            if len(error_info):
                return f"something wrong with the ideviceinfo: {error_info}"
        # idevicescreenshot check
        if not os.path.exists(IDEVICE_SCREENSHOT):
            return "idevicescreenshot command not found, check your libimobiledevice"
        else:
            screen_shot_file = os.path.abspath(os.path.join(IOS_SCREENSHOT_DIR, "test.jpg"))
            screen_info = subprocess.Popen(f"{IDEVICE_SCREENSHOT} {screen_shot_file}", shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            screen_info = screen_info.stdout.read().decode()
            if "Could not start screenshotr service" in screen_info:
                device_info = subprocess.Popen("ideviceinfo -k ProductVersion", shell=True, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                device_product_version = device_info.stdout.read().decode()
                if len(device_product_version.split(".")) == 3:
                    device_product_version = ".".join(device_product_version.split(".")[:-1])
                if os.path.exists(f"{DISKIMAGE_DIR}/{device_product_version}"):
                    subprocess.check_call(
                        ["ideviceimagemounter", f"{DISKIMAGE_DIR}/{device_product_version}/DeveloperDiskImage.dmg"])
                else:
                    target_developer_disk_url = f"{iOSDeveloperDiskImageUrl}/{device_product_version}.zip"
                    disk_path = download_file(target_developer_disk_url)
                    subprocess.check_call(["unzip", disk_path, "-d", DISKIMAGE_DIR])
                    subprocess.check_call(
                        ["ideviceimagemounter", f"{DISKIMAGE_DIR}/{device_product_version}/DeveloperDiskImage.dmg"])

    def take_screenshot(self, file_name="temp"):
        screen_shot_file = os.path.abspath(os.path.join(IOS_SCREENSHOT_DIR, f"{file_name}.jpg"))
        p = subprocess.run(f"{IDEVICE_SCREENSHOT} -u {self.device_id} {screen_shot_file}",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = {
            "returncode": p.returncode,
            "result": p,
            "screen_shot_file": screen_shot_file,
        }
        return result


if __name__ == '__main__':
    pass
