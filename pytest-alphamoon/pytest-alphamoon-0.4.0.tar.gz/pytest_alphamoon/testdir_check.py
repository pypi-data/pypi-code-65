# -*- coding: utf-8 -*-
"""
NOTE:
    This plugin should have been based on pytest's test discovery, but since this requires
    analysis of gathered tests at different pytest stage, for now plugin implements own
    discovery, which reports failure each time when function / class / file
    contains 'test' token without being under tests/ directory
"""
import os
import re

import pytest

TEST_FILE_PATTERNS = [
    r'test[\w]*\.py',
    r'[\w]*test\.py',
]

PLUGIN_NAME = 'testdir-check'
TESTS_REQUIRED_TOKEN_INI = 'tests_required_token'
DEFAULT_TEST_REQUIRED_TOKEN = {
    'tests',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check whether tests are placed under allowed directories")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform initial tests placement checks")

    parser.addini(TESTS_REQUIRED_TOKEN_INI, type='linelist', help=(
        "Each line specifies a single directory name, under which test files are allowed"
    ))


def pytest_sessionstart(session):
    config = session.config
    if config.getoption(PLUGIN_NAME):
        test_required_token = config.getini(TESTS_REQUIRED_TOKEN_INI)
        if test_required_token:
            config.test_required_token = test_required_token
        else:
            config.test_required_token = DEFAULT_TEST_REQUIRED_TOKEN


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and path.ext == '.py':
        return PyFile.from_parent(parent, fspath=path)


class PyFile(pytest.File):
    def collect(self):
        filename = self.fspath.basename
        rel_path = self.config.rootdir.bestrelpath(self.fspath)
        if any(re.match(pattern, filename) for pattern in TEST_FILE_PATTERNS):
            yield TestDirCheckItem.from_parent(self,
                                               name=str(self.fspath),
                                               rel_path=rel_path,
                                               test_required_token=self.config.test_required_token,
                                               )


class TestDirCheckItem(pytest.Item):
    def __init__(self, name, parent, rel_path, test_required_token):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._nodeid += f"::{PLUGIN_NAME}"
        self._rel_path = rel_path
        self._test_required_tokens = test_required_token

    def runtest(self):
        test_dir_err = self.check_test_dir()

        if test_dir_err:
            raise TestDirCheckError(self.fspath, test_dir_err)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(TestDirCheckError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_test_dir(self):
        path_components = self._rel_path.split(os.sep)
        if any(req_token in component for req_token in self._test_required_tokens for component in
               path_components):
            return ""
        return "Invalid test file placement"


class TestDirCheckError(Exception):
    """ Indicates error during checks of placement of test functions . """

    def __init__(self, path, err_message):
        self._path = path
        self._err_message = err_message

    def get_message(self):
        return f"{self._path}: {self._err_message}"
