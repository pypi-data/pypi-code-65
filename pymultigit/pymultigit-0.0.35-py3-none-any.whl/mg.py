import glob
import os
import os.path
import subprocess
import sys

import click
import git
from pyfakeuse.pyfakeuse import fake_use


def projects(sort: bool):
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


def run(args, do_exit=True):
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


class Obj:
    def __init__(self):
        self.stats = False  # type: bool
        self.verbose = False  # type: bool
        self.quiet = False  # type: bool
        self.sort = False  # type: bool
        self.phrase = ""  # type: str


def do_count(obj: Obj, fnc, attr_name, not_attr_name, attr_plural):
    count = 0
    count_attr = 0
    for (project_name, project_dir) in projects(sort=obj.sort):
        count += 1
        repo = git.Repo(project_dir)
        attr = fnc(repo)
        if attr:
            count_attr += 1
        if obj.verbose:
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
    if obj.stats:
        print('scanned [{count}] projects'.format(
            count=count,
        ))
        print('[{count_attr}] projects {attr_plural}'.format(
            count_attr=count_attr,
            attr_plural=attr_plural,
        ))


def do_for_all_projects(obj, fnc):
    count = 0
    count_not_found = 0
    count_error = 0
    count_ok = 0
    orig_dir = os.getcwd()
    for (project_name, project_dir) in projects(sort=obj.sort):
        if obj.verbose:
            print('doing [{0}] at [{1}]...'.format(project_name, project_dir), end='')
            sys.stdout.flush()
        count += 1
        if os.path.isdir(project_dir):
            os.chdir(project_dir)
            ret = fnc(obj, project_name, project_dir)
            if ret:
                count_error += 1
            else:
                count_ok += 1
            if obj.verbose:
                print('OK')
            os.chdir(orig_dir)
        else:
            if obj.verbose:
                print('NOT FOUND')
            count_not_found += 1
    if obj.stats:
        print('scanned [{}] projects'.format(count))
        print('[{}] not found'.format(count_not_found))
        print('[{}] error'.format(count_error))
        print('[{}] ok'.format(count_ok))


def is_dirty(repo):
    return repo.is_dirty()


def has_untracked_files(repo):
    return len(repo.untracked_files) > 0


def non_synchronized_with_upstream(repo):
    fake_use(repo)
    return False


def do_build(obj: Obj, project_name: str, project_dir: str):
    fake_use(project_name)
    makefile = os.path.join(project_dir, 'Makefile')
    bootstrap = os.path.join(project_dir, 'bootstrap')
    if os.path.isfile(makefile):
        pass
    if os.path.isfile(bootstrap):
        pass
    if obj.stats:
        pass


def do_pull(obj: Obj, project_name: str, project_dir: str):
    fake_use(project_name, project_dir)
    args = ['git', 'pull']
    if obj.verbose:
        args.append('--verbose')
    if obj.quiet:
        args.append('--quiet')
    return subprocess.call(args)


def do_grep(obj: Obj, project_name: str, project_dir: str):
    fake_use(project_name, project_dir)
    args = ['git', 'grep', obj.phrase]
    if obj.verbose:
        args.append('--verbose')
    if obj.quiet:
        args.append('--quiet')
    return subprocess.call(args)


def do_clean(obj: Obj, project_name: str, project_dir: str):
    fake_use(obj, project_name, project_dir)
    args = ['git', 'clean', '-ffxd']
    if obj.quiet:
        args.append('--quiet')
    return subprocess.call(args)


def do_status_msg(obj: Obj, project_name: str, msg: str):
    (res_out, res_err, return_code) = run([
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
        if obj.verbose:
            print(res_out, end='')
            print(res_err, end='')
        return 1
    (res_out, res_err, return_code) = run([
        'git',
        'rev-list',
        '--left-only',
        '--count',
        '@...@{upstream}',
    ])
    if res_out != '0\n' or res_err != '':
        print('project [{0}] is not synced'.format(project_name))
        if obj.verbose:
            print(res_out, end='')
            print(res_err, end='')
        return 1
    return 0


def do_status(obj: Obj, project_name: str, project_dir: str):
    fake_use(project_dir)
    return do_status_msg(obj=obj, project_name=project_name, msg='project [{project_name}] is dirty')


def do_dirty(obj: Obj, project_name: str, project_dir: str):
    fake_use(project_dir)
    return do_status_msg(obj=obj, project_name=project_name, msg='{project_name}')


def do_print(obj: Obj, project_name: str, project_dir: str):
    if obj.verbose:
        print(project_name, project_dir)
    else:
        print(project_name)
    return 0


@click.group(short_help="short help")
@click.option('--verbose/--no-verbose', default=False, is_flag=True, help='be verbose')
@click.option('--quiet/--no-quiet', default=False, is_flag=True, help='be quiet')
@click.option('--stats/--no-stats', default=False, is_flag=True, help='show statistics at the end')
@click.option('--sort/--no-sort', default=True, is_flag=True, help='sort project name')
@click.option('--phrase', default=None, is_flag=False, help='what to look for')
@click.pass_context
def cli(ctx, verbose, quiet, stats, sort, phrase):
    """ pymultigit allows you to perform operations on multiple git repositories """
    ctx.obj = Obj()
    ctx.obj.verbose = verbose
    ctx.obj.quiet = quiet
    ctx.obj.stats = stats
    ctx.obj.sort = sort
    ctx.obj.phrase = phrase


@cli.command()
@click.pass_obj
def dirty(obj):
    """ show the status of multiple git repositories """
    do_count(obj, is_dirty, 'is dirty', 'is clean', 'were dirty')


@cli.command()
@click.pass_obj
def untracked(obj):
    """ show which repositories have untracked files """
    do_count(obj, has_untracked_files, 'has untracked files', 'is fully tracked', 'have untracked files')


@cli.command()
@click.pass_obj
def synchronized(obj):
    """ show which repositories are synchronized with their upstream """
    do_count(obj, non_synchronized_with_upstream, 'is behind upstream', 'is synchronized', 'are behind upstream')


@cli.command()
@click.pass_obj
def clean(obj):
    """ clean all projects """
    do_for_all_projects(obj, do_clean)


@cli.command()
@click.pass_obj
def status(obj):
    """ show the status of multiple git repositories """
    do_for_all_projects(obj, do_status)


@cli.command()
@click.pass_obj
def dirty(obj):
    """ show names of project which are dirty """
    do_for_all_projects(obj, do_dirty)


@cli.command()
@click.pass_obj
def build(obj):
    """ build multiple git repositories """
    do_for_all_projects(obj, do_build)


@cli.command()
@click.pass_obj
def pull(obj):
    """ pull changes for multiple git repositories """
    do_for_all_projects(obj, do_pull)


@cli.command()
@click.pass_obj
def grep(obj):
    """ grep multiple repositories for pattern """
    do_for_all_projects(obj, do_grep)


@cli.command(name="list")
@click.pass_obj
def list_projects(obj):
    """ list all projects """
    do_for_all_projects(obj, do_print)


if __name__ == '__main__':
    cli()
