import os
import sys
import datetime
import hashlib
import time
import math


class Utils:
    KB = 1024
    MB = KB * KB
    CHUNK_SIZE = 10 * MB

    @staticmethod
    def eprint(*args, **kwargs):
        """Print to stderr"""
        print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def expand_path(local_path):
        var_path = os.path.expandvars(local_path)
        expanded_path = os.path.expanduser(var_path)
        return os.path.abspath(expanded_path)

    @staticmethod
    def ensure_dirs(local_path):
        """Ensures the directories in local_path exist.

        Args:
            local_path: The local path to ensure.

        Returns:
            None
        """
        if not os.path.isdir(local_path):
            os.makedirs(local_path)

    @staticmethod
    def timestamp_str():
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    @staticmethod
    def get_md5(local_path):
        start_time = time.time()
        print_progress = False
        total_size = None
        report_size = None

        md5 = hashlib.md5()
        with open(local_path, mode='rb') as fd:
            total_read = 0
            while True:
                chunk = fd.read(Utils.CHUNK_SIZE)
                if not chunk:
                    break
                md5.update(chunk)
                total_read += len(chunk)
                # Start showing progress after 1 seconds
                if not print_progress and time.time() - start_time >= 1:
                    print_progress = True
                    total_size = os.path.getsize(local_path)
                    report_size = total_read

                if print_progress and total_read % report_size == 0:
                    Utils.print_inplace('Reading {0} of {1} : {2}'.format(
                        Utils.pretty_size(total_read),
                        Utils.pretty_size(total_size),
                        local_path))
        if print_progress:
            Utils.print_inplace('')

        return md5.hexdigest()

    # Holds the last string that was printed
    __last_print_inplace_len = 0

    @staticmethod
    def print_inplace(msg):
        # Clear the line. Using this method so it works on Windows too.
        print(' ' * Utils.__last_print_inplace_len, end='\r')
        print(msg, end='\r')
        Utils.__last_print_inplace_len = len(msg)

    # Hold the names for pretty printing file sizes.
    PRETTY_SIZE_NAMES = ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    @staticmethod
    def pretty_size(size):
        if size > 0:
            i = int(math.floor(math.log(size, 1024)))
            p = math.pow(1024, i)
            s = round(size / p, 2)
        else:
            i = 0
            s = 0
        return '{0} {1}'.format(s, Utils.PRETTY_SIZE_NAMES[i])
