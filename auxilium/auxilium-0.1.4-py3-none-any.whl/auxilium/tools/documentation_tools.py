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


def api():
    print('*** run sphinx apidoc scripts ***')
    system("rm -f -r -v doc/sphinx/api")
    system("sphinx-apidoc -o doc/sphinx/api -f -E %s" % path.basename(getcwd()))
    print('INFO: Do not forget to add file under doc/sphinx/api to git (or your favourite scv).')
    print('')


def html():
    print('*** run sphinx html scripts ***')
    print('')
    system("sphinx-build -M clean ./doc/sphinx/ ./doc/sphinx/_build")
    system("sphinx-build -M html ./doc/sphinx/ ./doc/sphinx/_build")
    print('')


def latexpdf():
    print('*** run sphinx latexpdf scripts ***')
    print('')
    system("sphinx-build -M latexpdf ./doc/sphinx/ ./doc/sphinx/_build")
    print('')


def doctest():
    print('*** run sphinx doctest scripts ***')
    print('')
    system("sphinx-build -M doctest ./doc/sphinx/ ./doc/sphinx/_build")
    print('')


def show():
    html()
    system("open doc/sphinx/_build/html/index.html")


def sphinx():
    print('*** run sphinx scripts ***')
    print('')
    # api()
    html()
    doctest()
    print('')


