import subprocess
from typing import Any
from typing import Dict
from typing import List

from dict_tools import data

__virtualname__ = "cmd"


def _log_output(hub, stdout: str, stderr: str):
    for line in stdout.splitlines():
        hub.log.info(line)

    for line in stderr.splitlines():
        hub.log.debug(line)


def run(
    hub,
    cmd: List[str],
    shell: bool = False,
    timeout: int = None,
    fail_on_error: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    Run every command the same way
    :param hub:
    :param cmd:
    :param shell:
    :param timeout:
    :param fail_on_error:
    :return:
    """
    if shell is True and not isinstance(cmd, str):
        cmd = " ".join(cmd)
    elif shell is False and isinstance(cmd, str):
        cmd = cmd.split()

    proc = subprocess.Popen(
        cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs
    )

    retcode = proc.wait(timeout=timeout)

    stdout, stderr = proc.communicate(timeout=timeout)
    if isinstance(stdout, bytes):
        stdout = stdout.decode()
    if isinstance(stderr, bytes):
        stderr = stderr.decode()

    _log_output(hub, stdout, stderr)

    if retcode and fail_on_error:
        raise ChildProcessError(stderr)

    return data.NamespaceDict(
        retcode=retcode, stdout=stdout, stderr=stderr, pid=proc.pid
    )
