"""
    tests.integration.libvirt.test_pip_install
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the pip install of libvirt-python which needs to link to
    a system installed library
"""


def test_libvirt(project):
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "libvirt-python" not in ret.stdout

    ret = project.run("pip", "install", "libvirt-python")
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert "libvirt-python" in ret.stdout

    ret = project.run("pip", "uninstall", "-y", "libvirt-python")
    assert ret.exitcode == 0

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "libvirt-python" not in ret.stdout
