import os

import py
import pytest

PLUGIN_NAME = 'adr-check'
ADR_INI = 'adr_config_rel_path'
DEFAULT_ADR_PATH_DECLARATION = '.adr-dir'


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check consistent numbering Architecture Decision Record")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform ADR numbering checks",
    )

    parser.addini(ADR_INI, type='linelist', help=(
        "Specifies path containing ADR files"
    ))


def pytest_sessionstart(session):
    config = session.config
    if config.getoption(PLUGIN_NAME):
        adr_config_path = config.getini(ADR_INI)
        if adr_config_path:
            adr_config_path, *_ = adr_config_path
        else:
            adr_config_path = DEFAULT_ADR_PATH_DECLARATION

        with open(os.path.join(config.invocation_dir, adr_config_path), 'r') as f:
            config.adr_path = py.path.local(f.readline().rstrip('\n'))


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME):
        adr_path = config.adr_path
        if path.common(adr_path) == adr_path:
            return ADRFile.from_parent(parent, fspath=path)


class ADRFile(pytest.File):
    def collect(self):
        yield ADRNameCheckItem.from_parent(self, name=str(self.fspath))


class ADRNameCheckItem(pytest.Item):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)
        self.filename = self.fspath.basename

        self._adr_number = self._get_adr_number(self.filename)
        self._nodeid += f"::{PLUGIN_NAME}"

    def runtest(self):
        if self._check_duplication():
            raise ADRCheckError(self.filename)

    def _check_duplication(self):
        return sum(self._adr_number == self._get_adr_number(adr_name) for adr_name in
                   os.listdir(self.fspath.dirname)) > 1

    @staticmethod
    def _get_adr_number(adr_filename):
        adr_number, *_ = adr_filename.split('-')
        return adr_number

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(ADRCheckError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME


class ADRCheckError(Exception):
    """Indicates error during ADR numbering checks"""

    def __init__(self, adr_name):
        self._adr_filename = adr_name

    def get_message(self):
        msg = f"ADR file has non-unique id number: {self._adr_filename}"
        return msg
