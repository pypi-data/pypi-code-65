# -*- coding: utf-8 -*-
import os

import pytest

PLUGIN_NAME = 'init-check'
INIT_FORBIDDEN_INI = 'init_forbidden_in'
INIT_FILENAME = '__init__.py'
DEFAULT_INIT_FORBIDDEN_IN = {
    'scripts',
    'notebooks',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check forbidden __init__.py placement")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform checks for __init__.py presence in certain forbidden folders")

    parser.addini(INIT_FORBIDDEN_INI, type='linelist', help=(
        "Each line specifies a single directory name, under which __init__.py files are forbidden"
    ))


def pytest_sessionstart(session):
    """
    Checks whether there are names of directories, where __init__.py is forbidden,
    given in pytest.ini.
    In the case of lack of the forbidden imports specification, error is raised.
    """
    config = session.config
    if config.getoption(PLUGIN_NAME):
        ini_forbidden_inits = config.getini(INIT_FORBIDDEN_INI)
        if ini_forbidden_inits:
            config.ini_forbidden_inits = ini_forbidden_inits
        else:
            config.ini_forbidden_inits = DEFAULT_INIT_FORBIDDEN_IN


def pytest_collect_file(path, parent):
    config = parent.config

    if config.getoption(PLUGIN_NAME):
        return FileInForbiddenInitDir.from_parent(parent, fspath=path)


class FileInForbiddenInitDir(pytest.File):
    def collect(self):
        basename = os.path.basename(self.fspath.dirname)
        if basename in self.config.ini_forbidden_inits:
            yield InitCheckItem.from_parent(self,
                                            name=str(self.fspath),
                                            basename=basename,
                                            filename=self.fspath.basename,
                                            )


class InitCheckItem(pytest.Item):
    def __init__(self, name, parent, basename, filename):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._basename = basename
        self._filename = filename
        self._nodeid += f"::{PLUGIN_NAME}"

    def runtest(self):
        if self._filename == INIT_FILENAME:
            raise ForbiddenInitError(self.fspath, self._basename)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(ForbiddenInitError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME


class ForbiddenInitError(Exception):
    """ Indicates forbidden placement of __init__.py file. """

    def __init__(self, path, basename):
        self._path = path.dirname
        self._basename = basename

    def get_message(self):
        return f"{self._path}: {INIT_FILENAME} forbidden under {self._basename} directory"
