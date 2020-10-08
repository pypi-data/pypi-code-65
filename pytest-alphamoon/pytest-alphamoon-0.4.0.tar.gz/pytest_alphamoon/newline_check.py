# -*- coding: utf-8 -*-

import pytest

from pytest_alphamoon._commons import FileMatcher

PLUGIN_NAME = 'newline-check'
NEWLINE_REQUIRE_INI = 'newline_require'
DEFAULT_REQUIRED_NEWLINE_IN = {
    'requirements*',
    '.gitignore',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check whether newline exists at the end of certain files")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform checks on specified files whether there is newline present"
             " at the end of file")

    parser.addini('newline_require', type='linelist', help=(
        "Each line specifies a glob filename patter which will be checked against newline. "
        "Example: */requirements.txt"
    ))


def pytest_sessionstart(session):
    """
    Checks whether there are filename patters to be checked against newline, as specified by user
    If user specifies filenames, they overrides default ones!
    """
    config = session.config
    if config.getoption(PLUGIN_NAME):
        ini_newline_require = config.getini(NEWLINE_REQUIRE_INI)
        if ini_newline_require:
            config.require_newline = FileMatcher(ini_newline_require)
        else:
            config.require_newline = FileMatcher(DEFAULT_REQUIRED_NEWLINE_IN)


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and config.require_newline(path):
        return TextFile.from_parent(parent, fspath=path)


class TextFile(pytest.File):
    def collect(self):
        yield NewlineCheckItem.from_parent(self, name=str(self.fspath))


class NewlineCheckItem(pytest.Item):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._nodeid += f"::{PLUGIN_NAME}"

    def collect(self):
        return self

    def runtest(self):
        newline_err = self.check_newline()

        if newline_err:
            raise MissingNewlineError(self.name, newline_err)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(MissingNewlineError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_newline(self):
        """
        Performs newline checks and returns rule violation status. If file is empty, test is passed.
        Otherwise file is checked against occurrence of newline at the end and eventually
        against forbidden multiple newlines at the end
        """
        with open(self.fspath, 'r') as f:
            lines = f.readlines()
            if not lines:
                return False
            if lines[-1] == '\n':
                return "Extra newline(s) at the end of file"
            if not lines[-1].endswith('\n'):
                return "Missing newline at the end of file"
            return False


class MissingNewlineError(Exception):
    """ Indicates missing newline at the end of file."""

    def __init__(self, path, message):
        self._path = path
        self._message = message

    def get_message(self):
        return f"{self._path}: {self._message}"
