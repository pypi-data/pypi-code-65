import ast
import os
import sys
from collections import namedtuple
from contextlib import contextmanager

statement = namedtuple('Statement', ['code', 'line'])


class PyParser(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.parsed_stmts = []

    def parse_source(self):
        self.parsed_stmts = []
        with open(self.path, 'r') as src_code:
            ast_tree = ast.parse(src_code.read())
        self.visit(ast_tree)
        return self.parsed_stmts


class FileMatcher:
    """
    Class helps to maintain custom list of files
    Based on pytest-isort implementation:
        https://github.com/moccu/pytest-isort/blob/master/pytest_isort.py
    """

    def __init__(self, require_lines):
        self.requires = []

        for line in require_lines:
            comment_position = line.find("#")
            # Strip comments.
            if comment_position != -1:
                line = line[:comment_position]

            glob = line.strip()

            # Skip blank lines.
            if not glob:
                continue

            # Normalize path if needed.
            if glob and os.sep != '/' and '/' in glob:
                glob = glob.replace('/', os.sep)

            self.requires.append(glob)

    def __call__(self, path):
        for glob in self.requires:
            if path.fnmatch(glob):
                return glob


@contextmanager
def prepend_pythonpath(path):
    """
    :param path: path to be appended to PYTHONPATH at the first position
    :return: None
    :raises: ValueError, raised if PYTHONPATH doesn't include 'path' anymore
    """
    sys.path.insert(0, path)
    yield
    sys.path.remove(path)


def parse_lib(line):
    """Parses library declaration as library name and version. NOTE: version is required"""
    line = line.strip()
    if len(line) == 0 or line.startswith('#'):
        return None
    try:
        try:
            lib_name, version = line.split('==')
        except ValueError:
            lib_name, version = line, None
        return lib_name, version
    except ValueError:
        return None


def parse_requirements(requirements_lines):
    """Parses collection of requirements defined as library name and version"""
    parsed_libs = {}
    for i, line in enumerate(requirements_lines):
        parsed = parse_lib(line)
        if parsed is not None:
            lib_name, version = parsed
            parsed_libs[lib_name] = version
    return parsed_libs
