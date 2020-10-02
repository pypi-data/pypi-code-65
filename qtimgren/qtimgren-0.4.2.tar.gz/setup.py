#  Copyright (c) 2020 SBA - MIT License

from setuptools import setup
from warnings import warn

try:
    from setuptools_scm import get_version as scm_version
except ImportError:
    def scm_version(*_args, **_kwargs):
        raise LookupError

import os.path
import re
import subprocess

import sys

sys.path.append('.')

name = 'qtimgren'
wd = os.path.abspath(os.path.dirname(__file__))


def get_version() -> str:
    """ extract version number """
    _version = '0.0.0'  # fallback value should never be used
    try:  # first from git using setuptools_scm
        _version = scm_version(write_to=os.path.join(wd, name, 'version.py'))
    except LookupError:
        try:  # else from a previous version.py
            with open(os.path.join(wd, name, 'version.py')) as fd:
                for line in fd:
                    if line.startswith('version'):
                        _version = line.split("'")[1]
        except OSError:
            warn('Need either git+setuptools-scm or version.py file')
    return _version


def get_commit() -> str:
    try:
        p = subprocess.run('git show --format=%H -s', capture_output=True,
                           check=True, shell=True, encoding='Latin1')
    except (OSError, subprocess.CalledProcessError):
        return ''
    return p.stdout.strip()


def get_long_desc(_version) -> str:
    """ read long description and adjust master with version for badges or links
    only for release versions (x.y.z)
    """
    release = re.compile(r'(\d+\.){0,2}\d+$')
    with open(os.path.join(wd, 'README.md')) as fd:
        if _version == '0.0.0' or not release.match(_version):
            _long_description = fd.read()
        else:
            lines = fd.readlines()
            for i, line in enumerate(lines):
                if not line.startswith('['):
                    break
                if 'travis' in line:
                    lines[i] = line.replace('master', _version)
                elif 'codecov' in line:
                    commit = get_commit()
                    if commit != '':
                        lines[i] = line.replace('branch/master',
                                                'commit/' + commit)
            _long_description = ''.join(lines)
    return _long_description


if __name__ == '__main__':
    from tools.builder import BuildUi, BuildQm, BuildRc, build_py

    version = get_version()
    long_description = get_long_desc(version)
    setup(
        version=version,
        long_description=long_description,
        long_description_content_type='text/markdown',
        cmdclass={
            'build_ui': BuildUi,
            'build_qm': BuildQm,
            'build_rc': BuildRc,
            'build_py': build_py,
            'build_ext': build_py,
            'check': build_py,
        },
    )
