from .atom import Atom
from .logger import Logger
from .perf import Performance

import os
from shutil import rmtree
from pathlib import Path

_file_ = {'class': 'File', 'version': 3}
_folder_ = {'class': 'Folder', 'version': 3}

# ParentPathCreationNewFileNotFound
class ParentPathException(Exception):
    def __init__(self, File):
        File.log.error(f"Parent path not exist of  {File.red(File.__file__)}")


class File(Logger):

    def __init__(self, file_path, console=False):
        Logger.__init__(self, console=console, file_log= f'File.{file_path}')
        self._init_atom_register_class(_file_)

        self.__file__ = Path(file_path)

        opt_file = self.orange('looking')

        if not self.__file__.parent.exists():
            raise ParentPathException(self)

        if not self.__file__.exists():
            opt_file = self.green('new')
            with open(self.__file__, 'w') as fd:
                fd.write('')

        self.log.debug(f' File {opt_file} -> {self.violet(self.__file__)}')

    def folder(self):
        return self.__file__.parent

    def __str__(self):
        return str(self.__file__).strip()

    def read(self):
        with open(self.__file__, 'r') as f:
            return f.read()
    
    def write(self, data):
        with open(self.__file__, 'w') as f:
            return f.write(str(data))

    def append(self, data):
        with open(self.__file__, 'a') as f:
            return f.write(str(data))
    
    def remove(self):
        os.remove(self.__file__)


class Folder(Logger):

    def __init__(self, folder_path='./', console=False):
        Logger.__init__(self, console=console, file_log= f'Folder.{folder_path}')
        Atom.__init__(self, _folder_['class'], _folder_['version'])

        self.__folder__ = Path(folder_path)

        opt_folder = self.orange('looking')
        if not self.__folder__.parent.exists():
            raise ParentPathException(self)

        if not self.__folder__.exists():
            os.makedirs(self.__folder__, exist_ok=False)
            opt_folder = self.green('new')

        self.log.debug(f' Folder {opt_folder} -> {self.lightviolet(self.__folder__)}')

    @Performance.collect
    def folders(self):
        self.log.debug("call list_folder")
        return [x for x in self.__folder__.iterdir() if x.is_dir()]

    @Performance.collect
    def files(self):
        self.log.debug("call list_files")
        return [x for x in self.__folder__.iterdir() if x.is_file()]

    @Performance.collect
    def delete(self, target=None):
        if target is None:
            target = self.__folder__
        self.log.debug(f"call delete_folder on:\t{target}")
        rmtree(target)

    @Performance.collect
    def remove(self, target):
        self.log.debug(f"call delete_file on:\t{target}")
        os.remove(target)

    @Performance.collect
    def empty_folder(self):
        self.log.debug("call empty_folder")
        for folder in self.folders():
            self.delete(folder)
        for file in self.files():
            self.remove(file)
