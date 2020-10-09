import subprocess
import sys
import pytest


def test_add_model_help(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, 'add', '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' add [-h] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    ret = script_runner.run(pytest.aoa_script, 'add', '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' add [-h] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success


@pytest.mark.parametrize("command,params,input,want", [
    pytest.param("add", [],
                 b"Pytest Model\nThis is the Pytest Model description\n1\n0\n", {
                     "returncode": 0,
                     "stdout": b"Creating model structure for model:",
                     "stderr": b"",
                 }, id="Add model"),
    pytest.param("add", ['-error'],
                 b"", {
                     "returncode": 2,
                     "stdout": b"",
                     "stderr": b" error: unrecognized arguments: -error",
                 }, id="List error"),
])
def test_add_model(command, params, input, want):
    completed_process = run_add_model(command, params, input)
    got = {
        "returncode": completed_process.returncode,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
    }
    assert want['stderr'] in got['stderr']
    assert want['stdout'] in got['stdout']
    assert got['returncode'] == want['returncode']


def run_add_model(command, params, input):
    from subprocess import PIPE
    return subprocess.run(
        [sys.executable, pytest.aoa_script, command, *params, "-cwd={}".format(pytest.temp_dir)],
        input=input,
        stdout=PIPE,
        stderr=PIPE
    )
