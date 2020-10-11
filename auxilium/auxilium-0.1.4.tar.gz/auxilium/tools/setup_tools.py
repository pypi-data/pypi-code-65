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


from os import system, path, getcwd

import datetime
import os
import sys
import shutil
import zipfile


def create_project(name=None, slogan=None, author=None, email=None):
    loc = __file__.split(os.sep)
    loc[-2] = 'data'
    loc[-1] = 'pkg.zip'
    loc = os.sep.join(loc)

    print('Please enter project details.\n')

    if sys.version.startswith('2'):
        print("swap raw_input with input for python version %s" % sys.version)
        prompt_input = raw_input
    else:
        prompt_input = input

    name = prompt_input('Enter project name  : ') if name is None else name
    slogan = prompt_input('Enter project slogan: ') if slogan is None else slogan
    author = prompt_input('Enter author name   : ') if author is None else author
    email = prompt_input('Enter author email  : ') if email is None else email

    root_path = os.getcwd() + os.sep + name
    pkg_path = root_path + os.sep + name

    # setup project infrastructure
    if os.path.exists(root_path):
        raise FileExistsError('Project dir %s exists. Cannot create new project.' % root_path)

    # shutil.copytree(loc, root_path)
    with zipfile.ZipFile(loc, 'r') as zip_ref:
        zip_ref.extractall(root_path)

    os.makedirs(pkg_path)
    shutil.move(root_path + os.sep + '__init__.py', pkg_path)

    # setup source directory
    def rp(pth):
        f = open(pth, 'r')
        c = f.read()
        f.close()

        c = c.replace('<email>', email)
        c = c.replace('<author>', author)
        c = c.replace('<doc>', slogan)
        c = c.replace('<name>', name)
        c = c.replace('<date>', datetime.date.today().strftime('%A, %d %B %Y'))

        f = open(pth, 'w')
        f.write(c)
        f.close()

    rp(pkg_path + os.sep + '__init__.py')
    rp(root_path + os.sep + 'setup.py')
    rp(root_path + os.sep + 'README.rst')
    rp(root_path + os.sep + 'HOWTO.rst')
    rp(root_path + os.sep + 'CHANGES.rst')
    rp(root_path + os.sep + 'doc' + os.sep + 'sphinx' + os.sep + 'doc.rst')

    print('')
    print('Created project %s with these files:' % name)

    for subdir, dirs, files in os.walk(name):
        print('')
        for file in files:
            print('  ' + os.path.join(subdir, file))

    print('')
    print("Consider a first full run via: 'cd %s; auxilium full;'" % name)
    print('')


def setup():
    print('*** setup environment requirements ***')
    # print("pip freeze:")
    # python3 -m pip freeze)
    system("python3 -m pip freeze > freeze_requirements.txt")
    if path.exists("requirements.txt"):
        system("python3 -m pip install -r requirements.txt")

    if path.exists("upgrade_requirements.txt"):
        system("python3 -m pip install -r upgrade_requirements.txt")
    print('')


def install():
    print('*** install project via pip install -e ***')
    system("python3 -m pip install -e .")
    print('')


def upgrade():
    print('*** install project via pip install -e ***')
    system("python3 -m pip install --upgrade -e .")
    print('')


def uninstall():
    print('*** install project via pip uninstall ***')
    system("python3 -m pip uninstall -y %s" % path.basename(getcwd()))
    print('')


def cleanup():
    print('*** clean environment ***')

    # removed profiling data files
    system("rm -f -v .cprofile")

    # removed coverage data files
    system("rm -f -v .coverage")
    system("rm -f -v coverage.xml")
    system("rm -f -r -v htmlcov")

    # removed coverage data files from test/
    system("rm -f -v test/.coverage")
    system("rm -f -v test/coverage.xml")
    system("rm -f -r -v test/htmlcov")

    # remove bin files
    system("rm -f -r -v ./.bin/")

    # remove doc build files
    system("rm -f -r -v ./doc/sphinx/_build/")

    # remove setuptools release files
    system("rm -f -r -v ./build/")
    system("rm -f -r -v ./dist/")
    system("rm -f -r -v *.egg-info")
    system("rm -f -r -v .eggs")

    # 3. clean up afterwards
    # if [[ -s requirements.txt ]]; then
    #     python3 -m pip uninstall -y -r requirements.txt;
    # fi;
    # if [[ -s upgrade_requirements.txt ]]; then
    #     python3 -m pip uninstall -y -r upgrade_requirements.txt;
    # fi;
    # sed -i 's/==/>=/g' freeze_requirements.txt
    # if [[ -s freeze_requirements.txt ]]; then
    #     python3 -m pip install --upgrade -r freeze_requirements.txt;
    #     rm freeze_requirements.txt
    # fi;
    print('')


if __name__ == '__main__':
    create_project(*sys.argv[1:])
