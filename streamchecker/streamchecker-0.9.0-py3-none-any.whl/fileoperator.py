#! /usr/bin/env python3


import os
import json
import csv
import re
from pathlib import Path


class FileOperator():
    """Source file that contains items."""

    def __init__(self, path, filetype=False):
        """Initializes path."""

        self.__path = self.__resolvePath(path)
        self.__checkFile(self.__path)
        self.__filetype = self.__getFiletype(filetype)

    def __getFiletype(self, filetype):
        """Tries to guess the filetype from filename."""

        if filetype:
            ext = filetype
        else:
            reg = re.compile(r'.*\.([^\s^\.]+)$')
            if reg.match(str(self.__path)):
                ext = reg.match(str(self.__path)).groups()[0]
            else:
                ext = False
        return ext

    def __resolvePath(self, path):
        """Resolves path OS independently."""

        p = Path.resolve(Path.expanduser(Path(path)))
        return p

    def __checkFile(self, path):
        """Checks that file exists and creates it and path."""

        if not Path.exists(path):
            base = path.parents[0]
            if not Path.exists(base):
                os.makedirs(base)
                print(f"Created directory '{base}' for sources.")

            with open(path, 'a'):
                pass
            print(f"Created file '{path}' for sources.")

    def __fileEmpty(self, path):
        """Checks if file is empty."""

        if os.stat(path).st_size == 0:
            return True
        return False

    def loadFile(self, singleLayer=False):
        """Loads data from file.

        If given or guessed filetype is found then correct method is
        used to load data from file.

        Emptry string is returned if file is empty.

        Known filetypes: json, txt, csv.
        """

        if self.__fileEmpty(self.__path):
            return ''

        if self.__filetype == 'json':
            with open(self.__path, 'r') as f:
                data = json.load(f)

        elif self.__filetype == 'txt':
            with open(self.__path, 'r') as f:
                data = f.read()

        elif self.__filetype == 'csv':
            with open(self.__path, 'r', newline='') as f:
                csv_data = csv.reader(f, delimiter=',')
                data = list(csv_data)
            if singleLayer:
                data = [item for sublist in data for item in sublist]

        return data

    def saveFile(self, data=False):
        """Saves data to file.

        If given or guessed filetype is found then correct method is
        used to write given data.

        Empty data can be written to any filetype.

        Known filetypes: json, txt, csv.
        """

        if data:
            if self.__filetype == 'json':
                with open(self.__path, 'w') as f:
                    json.dump(data, f)

            elif self.__filetype == 'txt':
                with open(self.__path, 'w') as f:
                    f.write(data)

            elif self.__filetype == 'csv':
                with open(self.__path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(data)

        else:
            with open(self.__path, 'w') as f:
                f.write('')
