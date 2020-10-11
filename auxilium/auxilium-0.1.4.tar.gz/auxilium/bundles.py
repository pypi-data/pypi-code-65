# -*- coding: utf-8 -*-

# auxilium
# --------
# A Python project for an automated test and deploy toolkit - 100%
# reusable.
# 
# Author:   sonntagsgesicht
# Version:  0.1.4, copyright Sunday, 11 October 2020
# Website:  https://github.com/sonntagsgesicht/auxilium
# License:  Apache License 2.0 (see LICENSE file)


from os import path, getcwd

from .tools.setup_tools import setup, create_project
from .tools.test_tools import run, analysis, coverage, profile
from .tools.documentation_tools import sphinx
from .tools.deployment_tools import build, set_timestamp, replace_headers, release, pypideploy


def create():
    print('*** create new project ***')
    create_project()
    print('')


def simple():
    print("*** run simple test pipeline ***")
    setup()
    run()
    print('')
    print("*** run simple test pipeline finished ***")


def full():
    print("*** run full test pipeline ***")
    pkg_name = path.basename(getcwd())
    setup()
    sphinx()
    profile()
    analysis(pkg_name)
    coverage(pkg_name)
    # codecoverage(CODECOV_TOKEN)
    build()
    print('')
    print("*** run full test pipeline finished ***")


def deploy(github=None, pypi=None):
    print("*** run deployment pipeline ***")
    pkg_name = path.basename(getcwd())
    set_timestamp(pkg_name)
    replace_headers(pkg_name)
    build()
    if github:
        github_usr, github_pwd = github
        release(pkg_name, github_usr, github_pwd)
    if pypi:
        pypi_usr, pypi_pwd = pypi
        pypideploy(pypi_usr, pypi_pwd)
    print('')
    print("*** deployment pipeline finished ***")
