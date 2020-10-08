# -*- coding: utf-8 -*-
import re

import pytest

from pytest_alphamoon._commons import PyParser


class AnnotationRequirement:
    """Decorator requirement specification, read-only"""

    def __init__(self, required_by_dir_name, decorator_name):
        self.__name = decorator_name
        self.__required_by_dir_name = required_by_dir_name

    @property
    def name(self):
        return self.__name

    @property
    def required_by_dir_name(self):
        return self.__required_by_dir_name

    def __repr__(self):
        return (f"Required annotation '{self.name}' for each function/class "
                f"declaration under '/{self.required_by_dir_name}' directory")


PLUGIN_NAME = 'annotation-check'
DEFAULT_REQUIRED_ANNOTATIONS = [
    AnnotationRequirement('integration_tests', 'integration_test'),
]
TEST_CLASS_PREFIX = 'test'


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check required annotation for integration tests")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform initial decorator checks",
    )


def pytest_sessionstart(session):
    """
    Checks whether there are custom specification of decorator requirements
    """
    config = session.config
    config.decorator_requirements = DEFAULT_REQUIRED_ANNOTATIONS


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and path.ext == '.py':
        return PyFile.from_parent(parent, fspath=path)


class PyFile(pytest.File):
    def collect(self):
        required_annotations = []
        for r in self.config.decorator_requirements:
            rel_path = self.config.rootdir.bestrelpath(self.fspath)
            if re.match(r.required_by_dir_name, rel_path):
                required_annotations.append(r)

        if required_annotations:
            parser = AnnotationParser(self.fspath)
            class_func_declarations = parser.parse_source()
            for declaration_node in class_func_declarations:
                yield AnnotationCheckItem.from_parent(self,
                                                      name=declaration_node.name,
                                                      stmt_node=declaration_node,
                                                      required_annotations=required_annotations,
                                                      )


class AnnotationParser(PyParser):
    def visit_ClassDef(self, node):
        self.parsed_stmts.append(node)

    def visit_FunctionDef(self, node):
        self.parsed_stmts.append(node)


class AnnotationCheckItem(pytest.Item):
    """Checks annotation (for classes and/or for functions)"""

    def __init__(self, name, parent, stmt_node, required_annotations):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._node = stmt_node
        self._nodeid += f"::{PLUGIN_NAME}"
        self._required_annotations = required_annotations

    def runtest(self):
        missing_annotations = self.check_missing_annotation()
        if missing_annotations:
            raise AnnotationCheckError(str(self.fspath), missing_annotations)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(AnnotationCheckError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_missing_annotation(self):
        missing_annotations = []
        if self._node.name.lower().startswith(TEST_CLASS_PREFIX):
            node_decorators = self._node.decorator_list
            for dec_requirement in self._required_annotations:
                if not any(decorator.id == dec_requirement.name for decorator in node_decorators):
                    missing_annotations.append((self._node.lineno, dec_requirement))
        return missing_annotations


class AnnotationCheckError(Exception):
    """ Indicates error during annotation checks"""

    def __init__(self, path, missing_annotations):
        self._path = path
        self._missing_annotations = missing_annotations

    def get_message(self):
        msg = ""
        for line_num, violated_requirements in self._missing_annotations:
            msg += f"{self._path}:{line_num}: {violated_requirements}\n"
        return msg
