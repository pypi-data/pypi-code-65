#!/usr/bin/env python
# -*- coding: utf-8 -*0
"""Utilities."""


import os
import shutil
import subprocess


class Du:
    """Find and keep du command file path."""

    def __init__(self):
        """Initialize self."""
        self._path: str = ''

    @property
    def path(self) -> str:
        """Get qemu-img command file path.

        Returns
        -------
        str
            du command file path.

        Raises
        ------
        DuNotFoundException
            If shutil.which('du') returns None
        """
        if len(self._path) > 0:
            return self._path
        path_ = shutil.which('du')
        if path_ is None:
            raise DuNotFoundException()
        self._path = path_
        return self._path

    @path.setter
    def path(self, path_: str):
        """Force the result to the value.

        Set a string to force the result of self.path.

        If you set empty string, self.path will re-find the du path.

        Parameters
        ----------
        path_ : str
        """
        self._path = path_

    def get_usage(self, path_: str) -> int:
        """Get used amount of the file or directory.

        Parameters
        ----------
        path_ : str

        Returns
        -------
        int : used amount(bytes) of the file or directory
            Returns -1 if any error occurred.
        """
        if os.path.exists(path_) is False:
            return -1
        val = subprocess.check_output([self.path, '-s', '--block-size', '1', path_])
        val_split = val.split()
        val_bytes = val_split[0]
        val_str = val_bytes.decode('utf-8')
        val_int = int(val_str)
        return val_int


class DuNotFoundException(Exception):
    """An exception when du command not found in the PATH."""

    pass


def is_root() -> bool:
    """Return True if current user is root."""
    return True if os.getuid() == 0 else False


def get_mount_point_from_path(path_: str) -> str:
    """Find device mount point which contains specified path.

    Parameters
    ----------
    path_
        target path(file or dir.)

    Returns
    -------
        the device mount point which contains target path
    """
    # normalize
    current_path = os.path.realpath(path_)
    current_path = os.path.normcase(current_path)

    # query parent path and device id
    current_device_id = os.stat(current_path).st_dev
    parent_path = os.path.dirname(current_path)
    parent_device_id = os.stat(parent_path).st_dev

    # parent_path == current_path: top level dir.
    # parent_dev._id != current_dev._id:
    #     current_path is the mount point of the device

    while parent_path != current_path and \
            parent_device_id == current_device_id:
        # search upper dir.
        current_path = parent_path
        parent_path = os.path.dirname(current_path)
        current_device_id = parent_device_id
        parent_device_id = os.stat(parent_path).st_dev

    return current_path


def get_device_name_from_path(path_: str) -> str:
    """Get device name contains specified path.

    This function relies on Unix (uses /proc/mounts).

    Parameters
    ----------
    path_

    Returns
    -------
    device name contains specified path
    If path is invalid or cannot search, returns empty string.
    """
    mount_path = get_mount_point_from_path(path_)
    try:
        with open('/proc/mounts', 'r') as f:
            for s in f:
                p = s.rstrip('\n').split()
                if p[1] == mount_path:
                    return p[0]
    except EnvironmentError:
        pass
    return ''


def estimate_absolute_file_path(path_: str) -> str:
    """Estimate absolute file path from specified path string.

    This function searches an existing file from path.
    Unlike usual solutions, this function works for 'zipapp' relative path.

    At the case below:

        /opt/yourapp/

        * your_zipapp.zip
        * datafile.txt

    You can easily get full path of the 'datafile.txt'

    >>> print(estimate_absolute_file_path('datafile.ini'))
    /opt/yourapp/datafile.txt

    Parameters
    ----------
    path_ : str
        Relative path.

    Returns
    -------
    str
        The full path of the file.
        Returns empty string if founds no file.

    Examples
    --------
    ex1. based on relative path from program

        * /tmp/program.py
        * /tmp/a.txt

    >>> print(estimate_absolute_file_path('a.txt'))
    '/tmp/a.txt'

    ex2. based on relative path from current directory

        * /tmp/program.py
        * /foo/a.txt
        * $ cd /foo
        * $ /tmp/program.py

    >>> print(estimate_absolute_file_path('a.txt'))
    '/foo/a.txt'

    ex3. absolute path itself

        * /tmp/a.txt

    >>> print(estimate_absolute_file_path('/tmp/a.txt'))
    '/tmp/a.txt'

    """
    if os.path.isabs(path_):
        if os.path.isfile(path_):
            return path_
        return ''

    # relative path from current directory
    relative_path = os.path.join(os.path.abspath(os.getcwd()), path_)
    if os.path.isfile(relative_path):
        return path_

    # relative path of zipapp
    dir_ = os.path.dirname(os.path.abspath(__file__))
    dir_ = os.path.join(dir_, '..')
    relative_path = os.path.join(dir_, path_)
    if os.path.isfile(relative_path):
        return relative_path

    # relative path of normal script / zipapp internal
    dir_ = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(dir_, path_)
    if os.path.isfile(relative_path):
        return relative_path

    return ''
