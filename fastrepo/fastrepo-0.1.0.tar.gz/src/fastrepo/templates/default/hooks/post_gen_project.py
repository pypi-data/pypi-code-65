#!/usr/bin/env python
""" Hooks ran after project generation:

- remove_cli_dir: Remove the src/<PROJECT_SLUG>/cli directory when create_cli is set to False
"""
from pathlib import Path
from shutil import rmtree
from subprocess import check_call
import sys
from distutils.util import strtobool


PROJECT_SLUG: str = "{{ cookiecutter.project_slug }}"
CREATE_CLI: int = strtobool("{{ cookiecutter.create_cli }}")


def remove_cli_dir(should_create: bool) -> None:
    """ Remove the CLI directory when remove argument is True. """
    if not should_create:
        cli_subpackage = Path("src") / PROJECT_SLUG / "cli"
        rmtree(cli_subpackage)


def init_git() -> None:
    """ Init a git repository. """
    try:
        check_call(["git", "init"])
    except Exception:
        print("Error encountered during 'git init'. Do you have git installed ?", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":

    remove_cli_dir(CREATE_CLI)
    init_git()
