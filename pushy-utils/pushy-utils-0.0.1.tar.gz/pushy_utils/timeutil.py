from datetime import datetime
import time

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_timestamp():
    return time.time()


def get_timestamp_13():
    return int(round(time.time() * 1000))


def get_str_time(format=TIME_FORMAT):
    return datetime.fromtimestamp(time.time()).strftime(format)


def strftime(timestamp, format=TIME_FORMAT):
    return datetime.fromtimestamp(timestamp).strftime(format)


def strptime(str_time, format=TIME_FORMAT):
    datetime.strptime(str_time, format).timestamp()
