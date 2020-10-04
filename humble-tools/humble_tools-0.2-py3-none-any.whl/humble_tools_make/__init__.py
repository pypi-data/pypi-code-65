import os
from pathlib import Path
import shutil
from venv import create

import click
from click import Abort, ClickException
import pytest

from humble_tools.cli import cli


working_dir = Path()
flag_file = working_dir / '.htoolsrc'
venv_folder = working_dir / '.venv'
tests_folder = working_dir / 'tests'
source_path = working_dir / 'src'
dist_folder = working_dir / 'dist'
build_folder = working_dir / 'build'

python_venv_executable = venv_folder / 'bin' / 'python'


def check_if_current_folder_is_toolz_project():
    if not flag_file.exists():
        raise ClickException('Current directory is not a Humble Tools project.')


@cli.group()
def make():
    pass


@make.command()
def init():
    if flag_file.exists():
        raise ClickException('Project already initialized as a Humble Tools project.')

    if click.confirm('Initialize folder as Humble Tools project?'):
        flag_file.touch()
        click.echo('Folder initialized as Humble Tools project.')
    else:
        raise Abort('Doing nothing.')



@make.command()
def develop():
    check_if_current_folder_is_toolz_project()

    if venv_folder.exists():
        raise ClickException('Virtualenv folder already exists. Consider making clean first.')

    create(Path() / '.venv')


@make.command()
def clean():
    check_if_current_folder_is_toolz_project()

    shutil.rmtree(venv_folder, ignore_errors=True)
    shutil.rmtree(dist, ignore_errors=True)
    shutil.rmtree(build_folder, ignore_errors=True)


@make.command()
def test():
    check_if_current_folder_is_toolz_project()

    pytest.main([str(tests_folder),])


@make.command()
def ci():
    check_if_current_folder_is_toolz_project()

    pytest.main([
        f'--cov={source_path}',
        '--cov-report=xml:coverage.xml'
        ,'--junitxml=junit.xml',
        str(tests_folder)
    ])


@make.command()
def coverage():
    check_if_current_folder_is_toolz_project()

    pytest.main([
        f'--cov={source_path}',
        '--cov-report=term-missing',
        str(tests_folder)
    ])


@make.command()
def dist():
    check_if_current_folder_is_toolz_project()

    shutil.rmtree(build_folder, ignore_errors=True)
    shutil.rmtree(dist_folder, ignore_errors=True)

    os.system(f'{python_venv_executable} setup.py sdist')
