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


from os import system, chdir, getcwd, path

PROFILE_FILE = "dev.py"
TEST_DIR = "test"
CODECOV_TOKEN = ''


def run(test_dir=TEST_DIR):
    # 2. running actual test scripts
    print('*** run test scripts ***')
    # home = getcwd()
    # chdir(test_dir)
    # python3 -m unittest discover -v -s ${TEST_DIR} -p "*.py"
    system('python3 -m unittest discover %s -v -p "*.py"' % test_dir)
    # chdir(home)
    print('')


def test(test_dir=TEST_DIR):
    run(test_dir)


def profile(profile_file=PROFILE_FILE):
    print('*** run test profiling ***')
    system("python3 -m cProfile -s tottime %s" % profile_file)
    # python3 -m cProfile -o .cprofile ${PROFILE_FILE}
    # python3 -m pstats .cprofile stat
    # snakeviz .cprofile
    print('')


def analysis():
    print('*** run code analysis scripts ***')
    print('*** run pylint ***')
    system("pylint --exit-zero %s" % path.basename(getcwd()))
    # print('*** run flake8 ***')
    # flake8 --exit-zero "${NAME}";
    # print('*** run pycodestyle (aka pep8) ***')
    # pycodestyle "${NAME}";
    print('*** run bandit ***')
    system('bandit -r %s' % path.basename(getcwd()))
    print('')


def coverage(test_dir=TEST_DIR):
    print('*** run coverage scripts ***')
    home = getcwd()
    chdir(test_dir)
    cmd = 'python3 -m coverage run --include="*%s*" --omit="*test?.py"' % path.basename(getcwd())
    cmd += ' --module unittest discover -v -p "*.py"'
    system(cmd)
    system("python3 -m coverage xml")
    system("python3 -m coverage report")
    system("python3 -m coverage html")
    chdir(home)
    print('')


def codecoverage(token=CODECOV_TOKEN):
    print('*** run coverage scripts for codecov ***')
    system("coverage")
    system("codecov --token=%s" % token)
    print('')
