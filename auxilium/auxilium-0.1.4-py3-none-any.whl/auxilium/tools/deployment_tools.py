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


from datetime import date
from textwrap import wrap
from os import system, walk, sep, getcwd, linesep, path

# from requests import post


def set_timestamp(pkg, rootdir=getcwd()):
    pkg = __import__(pkg) if isinstance(pkg, str) else pkg

    for subdir, dirs, files in walk(rootdir):
        for file in files:
            if file.endswith('py'):
                file = path.join(subdir, file)

                # read file lines into list
                f = open(file, 'r')
                lines = list(map(str.rstrip, f.readlines()))
                f.close()

                # set library date
                if file == rootdir + sep + pkg.__name__ + sep + '__init__.py':
                    for i, line in enumerate(lines):
                        if line.startswith('__date__ = '):
                            print("set %s.__date__ = %s" % (pkg.__name__, date.today().strftime('%A, %d %B %Y')))
                            lines[i] = "__date__ = '" + date.today().strftime('%A, %d %B %Y') + "'"
                            break

                    f = open(file, 'w')
                    f.write(linesep.join(lines))
                    f.write(linesep)  # last empty line
                    f.close()


def replace_headers(pkg, rootdir=getcwd(), test=False):
    pkg = __import__(pkg) if isinstance(pkg, str) else pkg

    new_lines = pkg.__name__,
    new_lines += '-' * len(pkg.__name__),
    new_lines += tuple(wrap(pkg.__doc__))
    new_lines += '',
    new_lines += "Author:   " + pkg.__author__,
    new_lines += "Version:  " + pkg.__version__ + ', copyright ' + pkg.__date__,
    new_lines += "Website:  " + pkg.__url__,
    new_lines += "License:  " + pkg.__license__ + " (see LICENSE file)",
    new_header = ["# -*- coding: utf-8 -*-", ''] + ['# ' + l for l in new_lines] + ['', '']

    for subdir, dirs, files in walk(rootdir):
        for file in files:
            if file.endswith('py'):
                file = path.join(subdir, file)
                print('\n*** process %s ***\n' % file)

                # read file lines into list
                f = open(file, 'r')
                lines = list(map(str.rstrip, f.readlines()))
                f.close()

                # remove old header
                removed = list()
                while lines and (not lines[0] or lines[0].startswith('#')):
                    removed.append(lines.pop(0).strip())

                # add new header
                new_lines = new_header + lines

                if test:
                    print('remove : ' + '\nremove : '.join(removed[:20]))
                    print('-----------------------------------------------------------------')
                    print('add    : ' + '\nadd    : '.join(new_lines[:20]))
                else:
                    print('\n'.join(new_lines[:20]))
                    f = open(file, 'w')
                    f.write(linesep.join(new_lines))
                    f.write(linesep)  # last empty line
                    f.close()


def docmaintain():
    pkg_name = path.basename(getcwd())
    print('*** run docmaintain scripts ***')
    print('')
    set_timestamp(pkg_name)
    replace_headers(pkg_name)
    print('')


def build():
    print('*** run setuptools scripts ***')
    print('')
    system("python3 setup.py build")
    system("python3 setup.py sdist bdist_wheel")
    system("twine check dist/*")
    print('')


def repo():
    print('*** init a repository locally and on github.com ***')
    print('')
    print('-> command still under development <-')
    raise NotImplementedError()

    # git init ${NAME};
    # cd ${NAME};
    # git add -all;
    # git commit -m "Initial commit (via auxilium)";
    #
    # JSON='
    # {
    #   "name": "'"${NAME}"'",
    #   "description": "'"${SLOGAN}"'",
    #   "homepage": "https://github.com/"'"${GITHUB_USR}"'"/"'"${NAME}"'",
    #   "private": false,
    #   "has_issues": true,
    #   "has_projects": true,
    #   "has_wiki": true
    # }';
    # URL="https://api.github.com/${GITHUB_USR}/repos";
    # REMOTE="https://github.com/${GITHUB_USR}/${NAME}";
    #
    # print('')
    # print("curl -X POST ${URL}";
    # print(${JSON} >> repo.json
    # curl -u ${GITHUB_USR}:${GITHUB_PWD} -d "@repo.json" -X POST ${URL};
    # rm -f repo.json
    #
    # git fetch ${REMOTE};
    # git push;
    #
    # print('')


def release(github_user, github_pwd):
    print('*** draft release on github.com ***')
    print('')
    raise NotImplementedError()
    pkg = path.basename(getcwd())
    pkg = __import__(pkg) if isinstance(pkg, str) else pkg
    name = pkg.__name__
    version = 'v' + pkg.__version__
    msg = "update for release %s" % version

    # draft new GitHub release;
    data = {
        "tag_name": "'%s'" % version,
        "target_commitish": "master",
        "name": "'%s'" % version,
        "body": "'%s'" % msg,
        "draft": False,
        "prerelease": False
    }
    url = "https://api.github.com/repos/%s/%s/releases" % (github_user, name)
    # response = post(url, data=data, auth=(github_user, github_pwd))
    print(response)
    print('')


def pypideploy(pypi_usr, pypi_pwd):
    print('*** deploy release on pypi.org ***')
    print('')
    # run setuptools build
    system("python3 setup.py sdist bdist_wheel")
    system("python3 -m twine check dist/*")

    # push to PyPi.org
    cmd = "python3 -m twine upload -u %s -p %s" % (pypi_usr, pypi_pwd)
    cmd += " dist/* #--repository-url https://test.pypi.org/legacy/ dist/*"
    system(cmd)
    print('')


if __name__ == '__main__':
    # replace automated the header in source files
    pkg = path.basename(getcwd())
    set_timestamp(pkg)
    replace_headers(pkg)
