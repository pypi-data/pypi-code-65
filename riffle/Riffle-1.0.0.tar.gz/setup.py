# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import re
import subprocess
from distutils.spawn import find_executable

from setuptools import setup, find_packages, Command
from distutils.command.build import build as BuildCommand
from setuptools.command.install import install as InstallCommand
from distutils.command.clean import clean as CleanCommand
from setuptools.command.test import test as TestCommand
import distutils


ROOT_PATH = os.path.dirname(
    os.path.realpath(__file__)
)

SOURCE_PATH = os.path.join(
    ROOT_PATH, 'source'
)

RESOURCE_PATH = os.path.join(
    ROOT_PATH, 'resource'
)

RESOURCE_TARGET_PATH = os.path.join(
    SOURCE_PATH, 'riffle', 'resource.py'
)

README_PATH = os.path.join(ROOT_PATH, 'README.rst')

ON_READ_THE_DOCS = os.environ.get('READTHEDOCS', None) == 'True'

# Custom commands.
class BuildResources(Command):
    '''Build additional resources.'''

    user_options = []

    def initialize_options(self):
        '''Configure default options.'''

    def finalize_options(self):
        '''Finalize options to be used.'''
        self.resource_source_path = os.path.join(RESOURCE_PATH, 'resource.qrc')
        self.resource_target_path = RESOURCE_TARGET_PATH

    def run(self):
        '''Run build.'''
        if ON_READ_THE_DOCS:
            # PySide not available.
            return

        try:
            pyside_rcc_command = 'pyside2-rcc'

            # Check if the command for pyside2-rcc is in executable paths.
            pyside_rcc_executable_path = find_executable(pyside_rcc_command)
            if not pyside_rcc_executable_path:
                raise IOError(
                    'pyside2-rcc executable could not be found.'
                    'You might need to manually add it to your PATH.'
                )

            subprocess.check_call([
                pyside_rcc_executable_path,
                '-o',
                self.resource_target_path,
                self.resource_source_path
            ])

        except (subprocess.CalledProcessError, OSError):
            print(
                'Error compiling resource.py using pyside2-rcc. Possibly '
                'pyside2-rcc could not be found. You might need to manually add '
                'it to your PATH.'
            )
            raise SystemExit()


class Build(BuildCommand):
    '''Custom build to pre-build resources.'''

    def run(self):
        '''Run build ensuring build_resources called first.'''
        self.run_command('build_resources')
        BuildCommand.run(self)


class Install(InstallCommand):
    '''Custom install to pre-build resources.'''

    def do_egg_install(self):
        '''Run install ensuring build_resources called first.

        .. note::

            `do_egg_install` used rather than `run` as sometimes `run` is not
            called at all by setuptools.

        '''
        self.run_command('build_resources')
        InstallCommand.do_egg_install(self)


class Clean(CleanCommand):
    '''Custom clean to remove built resources and distributions.'''

    def run(self):
        '''Run clean.'''
        relative_resource_path = os.path.relpath(
            RESOURCE_TARGET_PATH, ROOT_PATH
        )
        if os.path.exists(relative_resource_path):
            os.remove(relative_resource_path)
        else:
            distutils.log.warn(
                '\'{0}\' does not exist -- can\'t clean it'
                .format(relative_resource_path)
            )

        relative_compiled_resource_path = relative_resource_path + 'c'
        if os.path.exists(relative_compiled_resource_path):
            os.remove(relative_compiled_resource_path)
        else:
            distutils.log.warn(
                '\'{0}\' does not exist -- can\'t clean it'
                .format(relative_compiled_resource_path)
            )
        CleanCommand.run(self)


class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


with open(os.path.join(SOURCE_PATH, 'riffle', '_version.py')) as _version_file:
    VERSION = re.match(
        r'.*__version__ = \'(.*?)\'',
        _version_file.read(),
        re.DOTALL
    ).group(1)


# Compute dependencies.
SETUP_REQUIRES = [
    'PySide2 >=5, < 6',
    'sphinx >= 2, < 4',
    'sphinx_rtd_theme >= 0.1.6, < 1',
    'lowdown >= 0.2.0, < 1',
    'mock >= 2, < 3'
]
INSTALL_REQUIRES = [
    'PySide2 >= 5, <6',
    'clique >= 2, < 3'
]
TEST_REQUIRES = [
    'pytest >= 2.3.5, < 5',
]


# Readthedocs requires Sphinx extensions to be specified as part of
# install_requires in order to build properly.
if ON_READ_THE_DOCS:
    INSTALL_REQUIRES.extend(SETUP_REQUIRES)

    # PySide not available.
    SETUP_REQUIRES = [
        requirement for requirement in SETUP_REQUIRES
        if not requirement.startswith("PySide2 ")
    ]

    INSTALL_REQUIRES = [
        requirement for requirement in INSTALL_REQUIRES
        if not requirement.startswith("PySide2 ")
    ]


setup(
    name='Riffle',
    version=VERSION,
    description='Filesystem browser for PySide.',
    long_description=open(README_PATH).read(),
    keywords='filesystem, browser, pyside, qt, pyqt',
    url='https://gitlab.com/4degrees/riffle',
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={
        '': 'source'
    },
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    extras_require={
        'setup': SETUP_REQUIRES,
        'tests': TEST_REQUIRES,
        'dev': SETUP_REQUIRES + TEST_REQUIRES
    },
    cmdclass={
        'build': Build,
        'build_resources': BuildResources,
        'install': Install,
        'clean': Clean,
        'test': PyTest
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    python_requires=">=3.0, <4.0"

)
