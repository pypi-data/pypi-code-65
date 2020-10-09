import subprocess
import sys
import pytest
import uuid

def test_clone_help(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, 'clone', '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' clone [-h] [-id PROJECT_ID] [-p PATH] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    ret = script_runner.run(pytest.aoa_script, 'clone', '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' clone [-h] [-id PROJECT_ID] [-p PATH] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success


@pytest.mark.parametrize("command,params,input,want", [
    pytest.param("clone", [],
                 b"0\n", {
                     "returncode": 1,
                     "stdout": b"already exists and is not an empty directory.",
                     "stderr": b"",
                 }, id="Clone model with no path"),
    pytest.param("clone", ['--path', '/tempita'],
                 b"0\n", {
                     "returncode": 1,
                     "stdout": b" could not create work tree dir '/tempita'",
                     "stderr": b"",
                 }, id="Clone model with wrong path"),
    # pytest.param("clone", ['--path', '/tmp/aoacli/' + str(uuid.uuid4()), '--test'],
    #              b"0\n", {
    #                  "returncode": 0,
    #                  "stdout": b"Project cloned at",
    #                  "stderr": b"",
    #              }, id="Clone model with path"),
    pytest.param("clone", ['-error'],
                 b"", {
                     "returncode": 2,
                     "stdout": b"",
                     "stderr": b" error: unrecognized arguments: -error",
                 }, id="Configure client error"),
])
def test_clone(command, params, input, want):
    completed_process = run_clone(command, params, input)
    got = {
        "returncode": completed_process.returncode,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
    }
    assert want['stderr'] in got['stderr']
    assert want['stdout'] in got['stdout']
    assert got['returncode'] == want['returncode']


def run_clone(command, params, input):
    from subprocess import PIPE
    return subprocess.run(
        [sys.executable, pytest.aoa_script, command, *params, "-cwd={}".format(pytest.temp_dir)],
        input=input,
        stdout=PIPE,
        stderr=PIPE
    )
