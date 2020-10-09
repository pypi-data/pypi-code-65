import subprocess
import sys
import pytest


def test_configure_help(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, 'configure', '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' configure [-h] [--repo] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    ret = script_runner.run(pytest.aoa_script, 'configure', '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' configure [-h] [--repo] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success


@pytest.mark.parametrize("command,params,input,want", [
    pytest.param("configure", ['--test'],
                 b"http://localhost:8080\n0\nadmin\nadmin\n", {
                     "returncode": 0,
                     "stdout": b"New configuration saved at",
                     "stderr": b"",
                 }, id="Configure client"),
    pytest.param("configure", ['--repo'],
                 b"0\n", {
                     "returncode": 0,
                     "stdout": b"Project configured.",
                     "stderr": b"",
                 }, id="Configure project"),
    pytest.param("configure", ['-error'],
                 b"", {
                     "returncode": 2,
                     "stdout": b"",
                     "stderr": b" error: unrecognized arguments: -error",
                 }, id="Configure client error"),
])
def test_configure(command, params, input, want):
    completed_process = run_configure(command, params, input)
    got = {
        "returncode": completed_process.returncode,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
    }
    assert want['stderr'] in got['stderr']
    assert want['stdout'] in got['stdout']
    assert got['returncode'] == want['returncode']


def run_configure(command, params, input):
    from subprocess import PIPE
    return subprocess.run(
        [sys.executable, pytest.aoa_script, command, *params, "-cwd={}".format(pytest.temp_dir)],
        input=input,
        stdout=PIPE,
        stderr=PIPE
    )
