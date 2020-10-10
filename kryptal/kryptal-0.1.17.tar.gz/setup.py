#!/usr/bin/env python
import subprocess

import sys

import os
from setuptools import setup, find_packages, Command


class MypyCommand(Command):
    description = 'Run MyPy type checker'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        command = ['mypy',
                   '--strict',
                   '--strict-equality',
                   '--disallow-incomplete-defs',
                   '--disallow-untyped-defs',
                   '--disallow-untyped-globals',
                   '--check-untyped-defs',
                   '--warn-unused-configs',
                   '--no-implicit-optional',
                   '--strict-optional',
                   '--warn-return-any',
                   '--warn-no-return',
                   '--warn-unreachable',
                   '--warn-unused-ignores',
                   '--warn-redundant-casts',
                   '--warn-incomplete-stub',
                   '--disallow-untyped-calls',
                   '--disallow-untyped-defs',
                   '--allow-subclassing-any',
                   '--allow-untyped-decorators',
                   '--local-partial-types',
                   '--no-implicit-reexport',
                   '--show-error-codes',
                   '--pretty',
                   'kryptal']
        myenv = os.environ.copy()
        myenv["MYPYPATH"] = "stubs/"
        returncode = subprocess.call(command, env=myenv)
        sys.exit(returncode)


dependencies = [
    'PyQT5 == 5.15.1',
    'yapsy == 1.12.2',
    'appdirs == 1.4.4',
    'mypy == 0.782',
    'typing_extensions == 3.7.4.3',
    'PyYAML == 5.3.1',
    'asyncqt == 0.8.0'
]

test_dependencies = [
    'nose == 1.3.7',
    'coverage == 5.3'
]

setup(name='kryptal',
      version='0.1.17',
      description='Manage encrypted file systems, for example to encrypt your cloud storage.',
      author='Sebastian Messmer',
      author_email='messmer@cryfs.org',
      license='GPLv3',
      url='https://github.com/cryfs/kryptal',
      cmdclass={
          'mypy': MypyCommand,
      },
      packages=find_packages(),
      package_data={
          'kryptal.gui': [
              '*.ui'
          ],
          'kryptal.gui.view': [
              '*.ui'
          ],
          'kryptal.gui.view.widgets': [
              '*.ui'
          ],
          'kryptal.gui.view.dialogs': [
              '*.ui'
          ],
          'kryptal.gui.view.icons': [
              '*'
          ],
          'kryptal.plugins.filesystems': [
              '*.kryptal-plugin'
          ],
          'kryptal.plugins.storageproviders': [
              '*.kryptal-plugin'
          ]
      },
      entry_points={
          'gui_scripts': [
              'kryptal = kryptal.gui.__main__:main'
          ]
      },
      install_requires=dependencies,
      tests_require=test_dependencies,
      # For CI, we need to have a way of installing test dependencies.
      # Let's abuse extras_require for that.
      extras_require={
          'test': test_dependencies
      },
      test_suite='nose.collector',
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Console",
          "Environment :: X11 Applications",
          "Environment :: X11 Applications :: Qt",
          "Operating System :: MacOS",
          "Operating System :: POSIX",
          "Operating System :: POSIX :: Linux",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Communications :: File Sharing",
          "Topic :: Security",
          "Topic :: Security :: Cryptography",
          "Topic :: System :: Filesystems",
          "Topic :: Utilities"
      ]
      )
