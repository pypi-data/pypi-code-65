""" Tasks for {{ cookiecutter.project_slug }} project. """

from pathlib import Path
from shutil import rmtree

from invoke import task


PROJECT_DIR = Path(__file__).parent
SRC_DIR = PROJECT_DIR / "src"
TESTS_DIR = PROJECT_DIR / "tests"

src_files = " ".join([str(path) for path in SRC_DIR.glob("**/*.py")])
test_files = " ".join([str(path) for path in TESTS_DIR.glob("**/*.py")])


@task
def doc(c):
    """ Serve the documentation. """
    c.run("mkdocs serve")


@task
def lint(c):
    """ Lint the code sources. """
    c.run(f"flake8 {src_files} {test_files} tasks.py")


@task
def format(c):
    """ Format the code sources. """

    c.run(f"black {src_files} {test_files} tasks.py")
    c.run(f"isort {src_files} {test_files} tasks.py")


@task
def build(c, doc=True):
    """ Build the user documentation. """
    if doc:
        c.run(f"mkdocs build -d {PROJECT_DIR / 'dist' / 'docs'}")
    c.run("poetry build")


@task
def clean(c):
    """ Clean the build artefacts. """
    try:
        rmtree(PROJECT_DIR / "dist")
    except FileNotFoundError:
        pass


@task
def test(c):
    """ Run the unit tests. """
    c.run("pytest")
