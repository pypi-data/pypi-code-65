#  Copyright (c) 2020  SBA - MIT License

import glob
import subprocess
from os.path import join
import os
import sys


def find_name():
    name = glob.glob('*.pro')[0][:-4]
    return name


def list_files():
    lst = glob.glob('*.qm')
    return lst


class Builder:
    def __init__(self, name=None):
        self.name = find_name() if name is None else name
        self.files = list_files()
        self.qrc = self.name + '.qrc'

    def write_qrc(self):
        with open(self.qrc, 'w') as out:
            out.write('<!DOCTYPE RCC>\n<RCC version="1.0">\n  <qresource prefix="/lang">\n')
            for file in self.files:
                splitted = file.rsplit('.', 1)[0].split('_', 1)
                name = splitted[1] if len(splitted) == 2 else file
                out.write('    <file alias="' + name + '">'
                          + file + '</file>\n')
            out.write('  </qresource>\n</RCC>\n')
        return self

    def build_resource(self):
        if len(self.files) > 0:
            self.write_qrc()
            subprocess.check_call(['pyside2-rcc', '-o',
                                   join('..', self.name, 'resource.py'),
                                   self.qrc], shell=True)
            os.remove(self.qrc)


if __name__ == '__main__':
    Builder(*sys.argv[1:]).build_resource()
