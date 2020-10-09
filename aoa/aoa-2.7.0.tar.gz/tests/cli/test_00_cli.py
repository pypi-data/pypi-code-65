import pytest


def test_help(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' [-h] [--debug] [--version]\n' in ret.stdout
    assert ret.stderr == ''
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' [-h] [--debug] [--version]\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    assert ret.success


def test_version(setup, script_runner):
    # Test display version
    from aoa import __version__
    ret = script_runner.run(pytest.aoa_script, '--version')
    assert ret.stdout =="\n{}\n".format(__version__)
    assert ret.stderr == ''
    assert ret.success
