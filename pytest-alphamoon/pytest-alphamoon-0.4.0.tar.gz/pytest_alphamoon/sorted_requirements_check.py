import pytest

from pytest_alphamoon._commons import FileMatcher

PLUGIN_NAME = 'sorted-requirements-check'
SORTED_REQUIREMENTS_INI = 'sorted_requirements'
SORTED_REQUIREMENTS_IN = {
    'requirements*',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        f"{PLUGIN_NAME}: Test to check whether requirement files are sorted")


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        f'--{PLUGIN_NAME}',
        dest=PLUGIN_NAME,
        action='store_true',
        help="Perform checks if requirement files are sorted")

    parser.addini(SORTED_REQUIREMENTS_INI, type='linelist',
                  help="Each line specifies file that consists of sections which should be sorted "
                       "alphabetically")


def pytest_sessionstart(session):
    config = session.config
    if config.getoption(PLUGIN_NAME):
        ini_sorted_requirements = config.getini(SORTED_REQUIREMENTS_INI)
        if ini_sorted_requirements:
            config.sorted_requirements = FileMatcher(ini_sorted_requirements)
        else:
            config.sorted_requirements = FileMatcher(SORTED_REQUIREMENTS_IN)


def pytest_collect_file(path, parent):
    config = parent.config
    if config.getoption(PLUGIN_NAME) and config.sorted_requirements(path):
        return TextFile.from_parent(parent, fspath=path)


class TextFile(pytest.File):
    def collect(self):
        yield SortedRequirementsCheckItem.from_parent(self, name=str(self.fspath))


class SortedRequirementsCheckItem(pytest.Item):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.add_marker(PLUGIN_NAME)

        self._nodeid += f"::{PLUGIN_NAME}"

    def collect(self):
        return self

    def runtest(self):
        sorted_requirements_err = self.check_sorted_requirements()

        if sorted_requirements_err:
            raise SortedRequirementsError(self.name, sorted_requirements_err)

    def repr_failure(self, exc_info, **kwargs):
        if exc_info.errisinstance(SortedRequirementsError):
            return exc_info.value.get_message()
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return self.fspath, -1, PLUGIN_NAME

    def check_sorted_requirements(self):
        with open(self.fspath, 'r') as f:
            file = f.readlines()

            section_idxs = [0] + \
                           [idx for idx, line in enumerate(file)
                            if not line.strip() or line.strip().startswith('#')] + \
                           [len(file) - 1]

            for id_range in zip(section_idxs[::2], section_idxs[1::2]):
                sublist = file[id_range[0]:id_range[1]]
                sublist = [elem.split('=')[0].split('<')[0].split('>')[0] for elem in sublist]
                if sublist != sorted(sublist):
                    return "File is not properly sorted"
            return False


class SortedRequirementsError(Exception):
    """ Indicates unsorted requirements. """

    def __init__(self, path, message):
        self._path = path
        self._message = message

    def get_message(self):
        return f"{self._path}: {self._message}"
