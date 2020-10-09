import subprocess
import sys
import pytest


def test_run_help(setup, script_runner):
    # Test display help message
    ret = script_runner.run(pytest.aoa_script, 'run', '-h')
    assert ret.stdout.startswith('usage: aoa')
    assert ' run [-h] [-id MODEL_ID] [-m MODE] [-d DATASET_ID]\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success
    ret = script_runner.run(pytest.aoa_script, 'run', '--help')
    assert ret.stdout.startswith('usage: aoa')
    assert ' run [-h] [-id MODEL_ID] [-m MODE] [-d DATASET_ID]\n' in ret.stdout
    assert ret.stderr == ''
    assert ret.success


@pytest.mark.parametrize("command,params,input,want", [
    pytest.param("run", [],
                 b"0\n0\n0\n", {
                     "returncode": 0,
                     "stdout": b"Loading and executing model code\nStarting training...\nFinished training\nSaved trained model\nArtefacts can be found in:",
                     "stderr": b"",
                 }, id="Train model with no parameters"),
    # pytest.param("run", ['-id', '03c9a01f-bd46-4e7c-9a60-4282039094e6', '-m', 'train', '-d', '11e1df4b-b630-47a1-ab80-7ad5385fcd8c'],
    #              b"", {
    #                  "returncode": 1,
    #                  "stdout": b"Loading and executing model code\nStarting training...\nFinished training\nSaved trained model\nArtefacts can be found in:",
    #                  "stderr": b"",
    #              }, id="Train model with parameters"),
    pytest.param("run", [],
                 b"0\n1\n0\n", {
                     "returncode": 0,
                     "stdout": b"Artefacts can be found in:",
                     "stderr": b"",
                 }, id="Evaluate model with no parameters"),
    # pytest.param("run", ['-id', '03c9a01f-bd46-4e7c-9a60-4282039094e6', '-m', 'evaluate', '-d', '11e1df4b-b630-47a1-ab80-7ad5385fcd8c'],
    #              b"", {
    #                  "returncode": 1,
    #                  "stdout": b"Evaluation metrics can be found in:",
    #                  "stderr": b"",
    #              }, id="Evaluate model with parameters"),
    pytest.param("run", ['-error'],
                 b"", {
                     "returncode": 2,
                     "stdout": b"",
                     "stderr": b" error: unrecognized arguments: -error",
                 }, id="Configure client error"),
])
def test_run(command, params, input, want):
    completed_process = run_run(command, params, input)
    got = {
        "returncode": completed_process.returncode,
        "stdout": completed_process.stdout,
        "stderr": completed_process.stderr,
    }
    assert want['stderr'] in got['stderr']
    assert want['stdout'] in got['stdout']
    assert got['returncode'] == want['returncode']


def run_run(command, params, input):
    from subprocess import PIPE
    return subprocess.run(
        [sys.executable, pytest.aoa_script, command, *params, "-cwd={}".format(pytest.temp_dir)],
        input=input,
        stdout=PIPE,
        stderr=PIPE
    )
