"""
    tests.integration.black.test_pip_install
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the pip install of black
"""
import subprocess

import pytest


@pytest.fixture
def built_project(project):
    # Build the tiamat package
    subprocess.run(
        ["tiamat", "--log-level=debug", "build", "-c", "build.conf"], cwd=project.path
    )
    import pathlib
    import shutil

    dst = pathlib.Path("/tmp") / "tiamatpip-build"
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(project.path, dst)
    return project


def test_black(built_project):
    built_project.run("pip", "install", "black")
    assert (
        "black"
        in built_project.run("pip", "list", stdout=subprocess.PIPE).stdout.decode()
    )

    built_project.run("pip", "uninstall", "-y", "black")
    assert (
        "black"
        not in built_project.run("pip", "list", stdout=subprocess.PIPE).stdout.decode()
    )
