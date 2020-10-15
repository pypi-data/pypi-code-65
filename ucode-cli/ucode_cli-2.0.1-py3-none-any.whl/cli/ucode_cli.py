import os
from datetime import datetime

import click

from ucode.helpers.clog import CLog
from ucode.services.dsa.problem_service import ProblemService
from ucode.ucode.ucode import UCode


@click.group()
def cli():
    """
    uCode.vn CLI tools - ucode CLI tools by Thuc Nguyen (https://github.com/thucnc)
    """
    click.echo("uCode.vn CLI tools - ucode CLI tools by Thuc Nguyen (https://github.com/thucnc)")


@cli.group(name='srv')
def ucode_group():
    """
    ucode server tools
    """
    click.echo("ucode server tools")


@cli.group(name='dsa')
def dsa_group():
    """
    DSA problem tools
    """
    click.echo("Common DSA tools")


@dsa_group.command(name='create')
@click.option('-d', '--dir', default='.',
              type=click.Path(file_okay=False),
              help='Base folder for the problem')
@click.option('-l', '--lang', default="vi", type=click.STRING, help='Main statement language')
@click.option('-t', '--trans', default="", type=click.STRING, help='Comma separated list of statement translation languages')
@click.option('--overwrite/--no-overwrite', default=False, help='Overwrite existing folder, default - No')
@click.argument('problem', metavar='{problem}')
def create_problem(dir, lang, trans, overwrite, problem):
    """
    Create a problem boilerplate

    Syntax:
    ucode dsa create -d {folder} {problem name} [--overwrite]

    Ex.:
    ucode dsa create "Race Condition"

    ucode dsa create -d problems -l en "Race Condition" --overwrite

    """
    tran_langs = trans.split(",")
    ProblemService.create_problem(dir, problem, lang=lang, translations=tran_langs, overwrite=overwrite)
    # print("DSA create")


@dsa_group.command(name='check')
@click.argument('problem_folder', metavar='{problem_folder}')
def check_problem(problem_folder):
    """
    Check problem folder for proper format

    Syntax:
    ptoolbox dsa check-problem {problem-folder}

    Ex.:
    ptoolbox dsa check-problem ../problems/prob2

    """
    ProblemService.check_problem(problem_folder)
    # print("DSA check")


@ucode_group.command(name="create")
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.option('-l', '--lesson', type=click.INT, help='Lesson id')
@click.option('-s', '--score', default=100, type=click.INT, help='Score of this question')
@click.option('-x', '--xp', default=100, type=click.INT, help='XP of this question')
@click.argument('problem_folder', metavar='{problem_folder}')
def ucode_create_problem(lesson, credential, score, problem_folder, xp):
    """
    Create problem on ucode.vn

    Syntax:
    ptoolbox ucode create-problem [--upload-testcases] -l {lesson_id} -s {score} {dsa_problem_folder}

    """
    api_url, token = UCode.read_credential(credential)
    if not api_url or not token:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    ucode = UCode(api_url, token)

    problem = ProblemService.load(problem_folder, load_testcase=True)
    problem_id = ucode.create_problem(lesson, problem, score=score, xp=xp)

    if problem:
        CLog.important(f'Problem `{problem_id}` created')


@ucode_group.command(name="create-multiple")
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.option('-l', '--lesson', type=click.INT, help='Lesson id')
@click.option('-s', '--score', default=100, type=click.INT, help='Score of this question')
@click.option('-x', '--xp', default=100, type=click.INT, help='XP of this question')
@click.argument('base_folder', metavar='{base_folder}')
def ucode_create_problems(lesson, credential, score, base_folder, xp):
    """
    Create multiple problems on ucode.vn

    Syntax:
    ptoolbox ucode create-problem [--upload-testcases] -l {lesson_id} -s {score} {dsa_problem_folder}

    """
    api_url, token = UCode.read_credential(credential)
    if not api_url or not token:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    ucode = UCode(api_url, token)

    problems = ProblemService.read_all_problems(base_folder, load_testcase=True)

    for problem_tuple in problems:
        problem = problem_tuple[1]
        problem_id = ucode.create_problem(lesson, problem, score=score, xp=xp)
        if problem:
            CLog.important(f'Problem `{problem_id}` created')
