#!/usr/local/bin/python3

"""
    Get camera devices by type (PT and IR)
"""

import subprocess

DEVICE_TYPES = ['PureThermal', 'USB 2.0 Camera']


class DeviceGetter:
    @staticmethod
    def get_usb_part__(line):
        # example: TODO
        return line.split(' ')[-1][1:-2]

    @staticmethod
    def get_usb_hub__(line):
        return line.split('-')[1].split('.')[0]

    @staticmethod
    def get_usb_port__(line):
        return line.split('-')[-1]

    @staticmethod
    def get_camera_device__(line):
        return line.replace('\t', '').replace('/dev/video', '')

    @staticmethod
    def get_camera_devices():
        result = subprocess\
            .run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE)\
            .stdout\
            .decode('utf-8')\
            .split('\n')

        groupped_by_device = {
            device: []
            for device in DEVICE_TYPES
        }
        for index, line in enumerate(result[:-1]):
            for device in DEVICE_TYPES:
                if device in line:
                    groupped_by_device[device].append({
                            'usb-hub': DeviceGetter.get_usb_hub__(DeviceGetter.get_usb_part__(line)),
                            'usb-port': DeviceGetter.get_usb_port__(DeviceGetter.get_usb_part__(line)),
                            'camera-device': DeviceGetter.get_camera_device__(result[index + 1]),
                    })

        for device in DEVICE_TYPES:
            groupped_by_device[device] = sorted(
                groupped_by_device[device],
                key=lambda item: (item['usb-hub'], item['usb-port']),
            )
            groupped_by_device[device] = [
                int(item['camera-device'])
                for item in groupped_by_device[device]
            ]

        return groupped_by_device
