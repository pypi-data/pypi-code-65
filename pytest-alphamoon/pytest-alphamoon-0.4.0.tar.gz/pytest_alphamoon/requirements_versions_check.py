import pytest

from pytest_alphamoon._commons import FileMatcher

PLUGIN_NAME = 'requirements-versions-check'
FIXED_REQUIREMENTS_INI = 'requirements_versions'
FIXED_REQUIREMENTS_VERSION_IN = {
    'requirements.txt',
    'requirements-dev.txt',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check whether requirements versions are fixed")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform checks if requirements versions are fixed")

    parser.addini(FIXED_REQUIREMENTS_INI, type='linelist',
                  help="Each line specifies file that consists of libraries which versions "
                       "should be fixed")


def pytest_sessionstart(session):
    config = session.config
    if config.getoption(PLUGIN_NAME):
        ini_requirements_versions = config.getini(FIXED_REQUIREMENTS_INI)
        if ini_requirements_versions:
            config.requirements_versions = FileMatcher(ini_requirements_versions)
        else:
            config.requirements_versions = FileMatcher(FIXED_REQUIREMENTS_VERSION_IN)


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and config.requirements_versions(path):
        return TextFile.from_parent(parent, fspath=path)


class TextFile(pytest.File):
    def collect(self):
        yield RequirementsVersionsCheckItem.from_parent(self, name=str(self.fspath))


class RequirementsVersionsCheckItem(pytest.Item):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._nodeid += f"::{PLUGIN_NAME}"

    def collect(self):
        return self

    def runtest(self):
        errors = self.check_requirements_versions()

        if errors:
            raise RequirementsVersionsError(self.name, errors)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(RequirementsVersionsError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_requirements_versions(self):
        errors = []
        with open(self.fspath, 'r') as f:
            for value in f:
                if value.strip() and not value.strip().startswith('#') and '=' not in value \
                        and '<' not in value and '>' not in value:
                    errors.append(value)
        if len(errors) > 0:
            return errors
        else:
            return False


class RequirementsVersionsError(Exception):
    """ Indicates which libraries don't have fixed versions. """

    def __init__(self, path, message):
        self._path = path
        self._message = message

    def get_message(self):
        msg = f"{self._path}: Libraries that versions are not fixed: "
        for lib in self._message:
            lib = lib.split('\n')[0]
            msg += f"{lib} "
        return msg
