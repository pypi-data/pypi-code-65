import subprocess
import sys
import pytest


def test_init_repo(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, 'init', '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' init [-h] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    ret = script_runner.run(pytest.aoa_script, 'init', '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' init [-h] [--debug]\n\noptional arguments:\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success


@pytest.mark.parametrize("command,params,input,want", [
    pytest.param("init", ['-h'],
                 b"", {
                     "returncode": 0,
                     "stdout": b" init [-h] [--debug]\n\noptional arguments:\n",
                     "stderr": b"",
                 }, id="Display help message with -h"),
    pytest.param("init", ['--help'],
                 b"", {
                     "returncode": 0,
                     "stdout": b" init [-h] [--debug]\n\noptional arguments:\n",
                     "stderr": b"",
                 }, id="Display help message with --help"),
    pytest.param("configure", ['--test'],
                 b"http://localhost:8080\n0\nadmin\nadmin\n", {
                     "returncode": 0,
                     "stdout": b"New configuration saved at",
                     "stderr": b"",
                 }, id="Configure client"),
    pytest.param("init", ['--debug'],
                 b"0\n", {
                     "returncode": 0,
                     "stdout": b"Creating model directory\nCreating model definitions\nmodel directory initialized at",
                     "stderr": b"",
                 }, id="Initialize project structure"),
    pytest.param("init", ['-error'],
                 b"", {
                     "returncode": 2,
                     "stdout": b"",
                     "stderr": b" error: unrecognized arguments: -error",
                 }, id="Init error"),
])
def test_init(command, params, input, want):
    completed_process = run_init(command, params, input)
    got = {
        "returncode": completed_process.returncode,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
    }
    assert want['stderr'] in got['stderr']
    assert want['stdout'] in got['stdout']
    assert got['returncode'] == want['returncode']


def run_init(command, params, input):
    from subprocess import PIPE
    return subprocess.run(
        [sys.executable, pytest.aoa_script, command, *params, "-cwd={}".format(pytest.temp_dir)],
        input=input,
        stdout=PIPE,
        stderr=PIPE
    )
