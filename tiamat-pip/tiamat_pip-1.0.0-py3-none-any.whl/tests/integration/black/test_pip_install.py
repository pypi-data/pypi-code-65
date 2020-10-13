"""
    tests.integration.black.test_pip_install
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the pip install of black
"""


def test_black(project):
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "black" not in ret.stdout

    ret = project.run("pip", "install", "black")
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert "black" in ret.stdout

    ret = project.run("pip", "uninstall", "-y", "black")
    assert ret.exitcode == 0

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "black" not in ret.stdout
