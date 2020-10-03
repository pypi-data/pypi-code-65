import glob
import os
import os.path
import subprocess
import sys
from typing import Tuple, Generator

import git
from pyfakeuse import fake_use

from pymultigit.configs import ConfigDebug, ConfigGrep


def projects(sort: bool) -> Generator[Tuple[str, str], None, None]:
    """
    the method returns tuples of (project_name, project_dir)
    """
    repos_list = glob.glob('*/.git')
    if sort:
        repos_list.sort()
    if len(repos_list) == 0:
        print('no git repos here', file=sys.stderr)
        sys.exit(1)
    for x in repos_list:
        yield os.path.dirname(x), os.path.dirname(x)


def run(args, do_exit=True) -> Tuple[str, str, int]:
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (res_out, res_err) = p.communicate()
    res_out = res_out.decode()
    res_err = res_err.decode()
    if p.returncode:
        print('errors while running [{0}]...'.format(args))
        print(res_out, end='', file=sys.stderr)
        print(res_err, end='', file=sys.stderr)
        if do_exit:
            sys.exit(p.returncode)
    return res_out, res_err, p.returncode


def do_count(fnc, attr_name, not_attr_name, attr_plural) -> None:
    count = 0
    count_attr = 0
    for (project_name, project_dir) in projects(sort=ConfigDebug.sort):
        count += 1
        repo = git.Repo(project_dir)
        attr = fnc(repo)
        if attr:
            count_attr += 1
        if ConfigDebug.verbose:
            if attr:
                print('project [{project_name}] {attr_name}'.format(
                    project_name=project_name,
                    attr_name=attr_name,
                ))
            else:
                print('project [{project_name}] {not_attr_name}'.format(
                    project_name=project_name,
                    not_attr_name=not_attr_name,
                ))
    if ConfigDebug.stats:
        print('scanned [{count}] projects'.format(
            count=count,
        ))
        print('[{count_attr}] projects {attr_plural}'.format(
            count_attr=count_attr,
            attr_plural=attr_plural,
        ))


def do_for_all_projects(fnc) -> None:
    count = 0
    count_not_found = 0
    count_error = 0
    count_ok = 0
    orig_dir = os.getcwd()
    for (project_name, project_dir) in projects(sort=ConfigDebug.sort):
        if ConfigDebug.verbose:
            print('doing [{0}] at [{1}]...'.format(project_name, project_dir), end='')
            sys.stdout.flush()
        count += 1
        if os.path.isdir(project_dir):
            os.chdir(project_dir)
            ret = fnc(project_name, project_dir)
            if ret:
                count_error += 1
            else:
                count_ok += 1
            if ConfigDebug.verbose:
                print('OK')
            os.chdir(orig_dir)
        else:
            if ConfigDebug.verbose:
                print('NOT FOUND')
            count_not_found += 1
    if ConfigDebug.stats:
        print('scanned [{}] projects'.format(count))
        print('[{}] not found'.format(count_not_found))
        print('[{}] error'.format(count_error))
        print('[{}] ok'.format(count_ok))


def is_dirty(repo) -> bool:
    return repo.is_dirty()


def has_untracked_files(repo) -> bool:
    return len(repo.untracked_files) > 0


def non_synchronized_with_upstream(repo) -> bool:
    fake_use(repo)
    return False


def do_build(project_name: str, project_dir: str) -> None:
    fake_use(project_name)
    makefile = os.path.join(project_dir, 'Makefile')
    bootstrap = os.path.join(project_dir, 'bootstrap')
    if os.path.isfile(makefile):
        pass
    if os.path.isfile(bootstrap):
        pass
    if ConfigDebug.stats:
        pass


def do_pull(project_name: str, project_dir: str) -> int:
    fake_use(project_name, project_dir)
    args = ['git', 'pull']
    if ConfigDebug.git_verbose:
        args.append('--verbose')
    if ConfigDebug.git_quiet:
        args.append('--quiet')
    return subprocess.call(args)


def do_grep(project_name: str, project_dir: str) -> None:
    fake_use(project_name, project_dir)
    args = ['git', 'grep', ConfigGrep.regexp]
    if ConfigDebug.git_verbose:
        args.append('--verbose')
    if ConfigDebug.git_quiet:
        args.append('--quiet')
    # return subprocess.call(args)
    pipe = subprocess.Popen(
        args,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for line in pipe.stdout:
        print("{}/{}".format(project_dir, line), end="")
    if pipe.returncode:
        raise subprocess.CalledProcessError(
            returncode=pipe.returncode,
            cmd=' '.join(args),
        )


def do_clean(project_name: str, project_dir: str) -> int:
    fake_use(project_name, project_dir)
    args = ['git', 'clean', '-ffxd']
    if ConfigDebug.git_verbose:
        args.append('--verbose')
    if ConfigDebug.git_quiet:
        args.append('--quiet')
    return subprocess.call(args)


def do_status_msg(project_name: str, msg: str) -> int:
    (res_out, res_err, _) = run([
        'git',
        'status',
        # porcelain is guaranteed to have parsable output and not
        # change across git versions
        '--porcelain',
        # when using --porcelain branch information is not shown,
        # this flag makes it not so, the problem with it is that
        # it produces output which should be parsed and that is
        # why we do not used it and use the 'git rev-list' that follows...
        # '--branch'
        # '--short',
    ])
    if res_out != '' or res_err != '':
        print(msg.format(project_name=project_name))
        if ConfigDebug.verbose:
            print(res_out, end='')
            print(res_err, end='')
        return 1
    (res_out, res_err, _) = run([
        'git',
        'rev-list',
        '--left-only',
        '--count',
        '@...@{upstream}',
    ])
    if res_out != '0\n' or res_err != '':
        if ConfigDebug.terse:
            msg = project_name
        else:
            msg = 'project [{}] is not synced'.format(project_name)
        print(msg)
        if ConfigDebug.verbose:
            print(res_out, end='')
            print(res_err, end='')
        return 1
    return 0


def do_status(project_name: str, project_dir: str) -> int:
    fake_use(project_dir)
    if ConfigDebug.terse:
        msg = "{project_name}"
    else:
        msg = 'project [{project_name}] is dirty'
    return do_status_msg(project_name=project_name, msg=msg)


def do_dirty(project_name: str, project_dir: str) -> int:
    fake_use(project_dir)
    return do_status_msg(project_name=project_name, msg='{project_name}')


def do_print(project_name: str, project_dir: str) -> None:
    if ConfigDebug.verbose:
        print(project_name, project_dir)
    else:
        print(project_name)
