# -*- coding: utf-8 -*-
import json

import pytest

PLUGIN_NAME = 'notebook-check'
NOTEBOOK_ALLOWED_INI = 'notebook_allowed_in'
JUPYTER_NOTEBOOK = '.ipynb'
DEFAULT_NOTEBOOK_ALLOWED = {
    'notebooks',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check notebooks are cleaned and under allowed directories")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform checks whether notebooks has been cleaned"
             " and are placed under proper (specified) directory")

    parser.addini(NOTEBOOK_ALLOWED_INI, type='linelist', help=(
        "Each line specifies a single directory name, under which jupyter notebooks might be placed"
    ))


def pytest_sessionstart(session):
    """
    Checks whether in pytest.ini directory names, where jupyter notebooks are allowed, was provided
    In the case of lack of the notebooks directory names specification, error is raised.
    """
    config = session.config
    if config.getoption(PLUGIN_NAME):
        ini_allowed_notebook_dirs = config.getini(NOTEBOOK_ALLOWED_INI)
        if ini_allowed_notebook_dirs:
            config.ini_allowed_notebook_dirs = ini_allowed_notebook_dirs
        else:
            config.ini_allowed_notebook_dirs = DEFAULT_NOTEBOOK_ALLOWED


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and path.ext == JUPYTER_NOTEBOOK:
        return NotebookFile.from_parent(parent, fspath=path)


class NotebookFile(pytest.File):
    def collect(self):
        yield NotebookCheckItem.from_parent(self, name=str(self.fspath))


class NotebookCheckItem(pytest.Item):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._nodeid += f"::{PLUGIN_NAME}"

    def runtest(self):
        error_messages = []
        dir_error = self.check_notebook_dir()
        if dir_error:
            error_messages.append(dir_error)

        output_error = self.check_notebook_output()
        if output_error:
            error_messages.append(output_error)

        if error_messages:
            raise NotebookCheckError(self.name, error_messages)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(NotebookCheckError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_notebook_dir(self):
        allowed_dirs = self.config.ini_allowed_notebook_dirs
        if not any(name in self.fspath.strpath for name in allowed_dirs):
            return f"notebook not under one of allowed directories: {allowed_dirs}"
        return ""

    def check_notebook_output(self):
        with open(self.fspath, 'r') as notebook_file:
            notebook = json.load(notebook_file)
            for cell in notebook['cells']:
                if (cell.get('ExecuteTime') is not None or
                        cell.get('execution_count') is not None or
                        cell.get('outputs')):
                    return "notebook with output"
        return ""


class NotebookCheckError(Exception):
    """ Indicates incorrect .ipnyb file placement. """

    def __init__(self, path, error_messages):
        self._path = path
        self._error_messages = error_messages

    def get_message(self):
        return f"'{self._path}: {', '.join(self._error_messages)}\n'"
