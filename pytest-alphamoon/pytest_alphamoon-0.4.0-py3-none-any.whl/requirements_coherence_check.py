import importlib
import os
from collections import defaultdict

import pytest

from pytest_alphamoon._commons import FileMatcher, parse_requirements, prepend_pythonpath

PLUGIN_NAME = 'requirements-coherence-check'
REQUIREMENTS_PATHS_INI = 'requirements_path'
SETUP_BASE_REQUIREMENTS_INI = 'base_requirements_collection'
SETUP_EXTRAS_REQUIREMENTS_INI = 'extras_requirements_collection'

SETUP_IMPORT_NAME = 'setup'
REQUIREMENTS_PATHS_DEFAULT = {
    'requirements.txt',
    'requirements-dev.txt',
}
SETUP_BASE_REQUIREMENTS_DEFAULT = 'install_requires'
SETUP_EXTRAS_REQUIREMENTS = 'extras'


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check whether requirements[-dev].txt are the same "
        "as those specified in setup.py")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform checks if requirements[-dev].txt are the same as setup.py")

    parser.addini(REQUIREMENTS_PATHS_INI, type='linelist',
                  help="Each line specifies requirements file")
    parser.addini(SETUP_BASE_REQUIREMENTS_INI, type='args',
                  help="Name of the collection specyfing basic requirements: "
                       "named install_requires in setuptools")
    parser.addini(SETUP_EXTRAS_REQUIREMENTS_INI, type='args',
                  help="Name of the collection specyfing basic requirements: "
                       "named extras_require in setuptools")


def pytest_sessionstart(session):
    config = session.config
    if config.getoption(PLUGIN_NAME):
        requirements_paths = config.getini(REQUIREMENTS_PATHS_INI)

        config.requirements_paths = FileMatcher(requirements_paths or REQUIREMENTS_PATHS_DEFAULT)
        config.setup_requirements = get_setup_requirements(
            config.getini(SETUP_BASE_REQUIREMENTS_INI) or SETUP_BASE_REQUIREMENTS_DEFAULT,
            config.getini(SETUP_EXTRAS_REQUIREMENTS_INI) or SETUP_EXTRAS_REQUIREMENTS
        )


def get_setup_requirements(setup_base_requirements_name, setup_extras_requirements_name):
    with prepend_pythonpath(os.getcwd()):
        install_requires = getattr(importlib.import_module(SETUP_IMPORT_NAME),
                                   setup_base_requirements_name)

        extras = getattr(importlib.import_module(SETUP_IMPORT_NAME),
                         setup_extras_requirements_name)

    all_requirements = install_requires + extras['all']
    all_requirements = set(all_requirements)
    return parse_requirements(all_requirements)


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and config.requirements_paths(path):
        return RequirementsFile.from_parent(parent, fspath=path)


class RequirementsFile(pytest.File):
    def collect(self):
        yield RequirementsCoherenceCheck.from_parent(
            self,
            name=str(self.fspath),
            setup_requirements=self.config.setup_requirements
        )


class RequirementsCoherenceCheck(pytest.Item):
    def __init__(self, name, parent, setup_requirements):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)
        self.setup_requirements = setup_requirements

        self._nodeid += f"::{PLUGIN_NAME}"

    def collect(self):
        return self

    def runtest(self):
        errors = self.check_requirements_versions()

        if errors:
            raise RequirementsCoherenceError(self.name, errors)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(RequirementsCoherenceError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_requirements_versions(self):
        errors = defaultdict(list)
        with open(self.fspath, 'r') as f:
            target_requirements = parse_requirements(f.readlines())
            for lib_name, lib_version in target_requirements.items():
                if lib_name not in self.setup_requirements.keys():
                    errors['missing_requirements'].append(lib_name)
                elif lib_version != self.setup_requirements[lib_name]:
                    errors['incoherent_versions'].append(
                        (lib_name, lib_version, self.setup_requirements[lib_name]))
        if len(errors) > 0:
            return errors
        else:
            return False


class RequirementsCoherenceError(Exception):
    """ Indicates which libraries are incoherent across setup.py and requirements[-dev].txt. """

    def __init__(self, path, message_content):
        self._path = path
        self._message_content = message_content

    def get_message(self):
        msg = ""
        if self._message_content['missing_requirements']:
            msg = f"{self._path}: Missing libraries in {SETUP_IMPORT_NAME}.py: "
            msg += ", ".join(self._message_content['missing_requirements'])

        if self._message_content['incoherent_versions']:
            msg += f"\n{self._path}: Libraries that has incoherent versions:\n"
            for lib, target_version, setup_version in self._message_content['incoherent_versions']:
                msg += (f"\t- [Requirements] '{lib}' "
                        f"{target_version} != {setup_version} [setup.py]\n")
        return msg
