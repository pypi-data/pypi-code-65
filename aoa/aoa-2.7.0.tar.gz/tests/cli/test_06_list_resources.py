import subprocess
import sys
import pytest


def test_list_resources_help(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, 'list', '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' list [-h] [--debug] [-p] [-m] [-lm] [-d]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    ret = script_runner.run(pytest.aoa_script, 'list', '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' list [-h] [--debug] [-p] [-m] [-lm] [-d]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success

    ret = script_runner.run(pytest.aoa_script, 'list', '-p', "-cwd={}".format(pytest.temp_dir))
    assert 'List of projects:' in ret.stdout
    assert ret.stderr == ''
    assert ret.success


@pytest.mark.parametrize("command,params,input,want", [
    pytest.param("list", ['-p'],
                 b"", {
                     "returncode": 0,
                     "stdout": b"\nList of projects:\n-----------------\n[0]",
                     "stderr": b"",
                 }, id="List projects"),
    pytest.param("list", ['-m'],
                 b"0\n", {
                     "returncode": 0,
                     "stdout": b"\nList of models for project",
                     "stderr": b"",
                 }, id="List models"),
    pytest.param("list", ['-lm'],
                 b"", {
                     "returncode": 0,
                     "stdout": b"\nList of local models:\n---------------------\n",
                     "stderr": b"",
                 }, id="List local models"),
    pytest.param("list", ['-d'],
                 b"0\n", {
                     "returncode": 0,
                     "stdout": b"\nList of datasets for project",
                     "stderr": b"",
                 }, id="List datasets"),
    pytest.param("list", ['-error'],
                 b"", {
                     "returncode": 2,
                     "stdout": b"",
                     "stderr": b" error: unrecognized arguments: -error",
                 }, id="List error"),
])
def test_list_resources(command, params, input, want):
    completed_process = run_list_resources(command, params, input)
    got = {
        "returncode": completed_process.returncode,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
    }
    assert want['stderr'] in got['stderr']
    assert want['stdout'] in got['stdout']
    assert got['returncode'] == want['returncode']


def run_list_resources(command, params, input):
    from subprocess import PIPE
    return subprocess.run(
        [sys.executable, pytest.aoa_script, command, *params, "-cwd={}".format(pytest.temp_dir)],
        input=input,
        stdout=PIPE,
        stderr=PIPE
    )
