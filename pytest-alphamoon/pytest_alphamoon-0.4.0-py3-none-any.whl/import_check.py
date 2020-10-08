# -*- coding: utf-8 -*-

import pytest

from pytest_alphamoon._commons import PyParser, statement

PLUGIN_NAME = 'import-check'
FORBIDDEN_IMPORT_INI = 'import_forbidden_from'
DEFAULT_IMPORTS_FORBIDDEN_FROM = {
    'scripts',
    'user_settings',
    'notebooks',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check violation of forbidden imports")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform initial import checks")

    parser.addini(FORBIDDEN_IMPORT_INI, type='linelist', help=(
        "Each line specifies a single name (e.g. module name), from which imports are forbidden"
    ))


def pytest_sessionstart(session):
    """
    Checks whether there are names of imports given in pytest.ini.
    In the case of lack of the forbidden imports specification, error is raised.
    """
    config = session.config
    if config.getoption(PLUGIN_NAME):
        ini_forbidden_imports = config.getini(FORBIDDEN_IMPORT_INI)
        if ini_forbidden_imports:
            config.ini_forbidden_imports = ini_forbidden_imports
        else:
            config.ini_forbidden_imports = DEFAULT_IMPORTS_FORBIDDEN_FROM


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and path.ext == '.py':
        return PyFile.from_parent(parent, fspath=path)


class PyFile(pytest.File):
    def collect(self):
        import_statements = ImportParser(self.fspath).parse_source()
        for stmt in import_statements:
            yield ImportCheckItem.from_parent(self, name=str(stmt.line), import_statement=stmt.code)


class ImportParser(PyParser):
    def visit_Import(self, node):
        for stmt in node.names:
            self.parsed_stmts.append(statement(stmt.name, node.lineno))

    def visit_ImportFrom(self, node):
        self.parsed_stmts.append(statement(node.module, node.lineno))
        for stmt in node.names:
            self.parsed_stmts.append(statement(stmt.name, node.lineno))


class ImportCheckItem(pytest.Item):
    def __init__(self, name, parent, import_statement):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._import_statement = import_statement
        self._nodeid += f"::{PLUGIN_NAME}"

    def runtest(self):
        violating_imports = []
        for forbid_import in self.config.ini_forbidden_imports:
            if forbid_import in self._import_statement.split('.'):
                violating_imports.append((self.name, forbid_import))

        if violating_imports:
            raise ImportCheckError(str(self.fspath), violating_imports)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(ImportCheckError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME


class ImportCheckError(Exception):
    """ Indicates error during import checks. """

    def __init__(self, path, violating_import_stmt):
        self._path = path
        self._forbidden_imports = violating_import_stmt

    def get_message(self):
        msg = ''
        for line_num, import_type in self._forbidden_imports:
            msg += f"{self._path}:{line_num}: imports from {import_type} are forbidden\n"
        return msg
