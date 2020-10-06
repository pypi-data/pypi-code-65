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

    proc = subprocess.run(
        cmd,
        shell=shell,
        timeout=timeout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        **kwargs,
    )
    _log_output(hub, proc.stdout, proc.stderr)

    if fail_on_error:
        proc.check_returncode()

    return data.NamespaceDict(
        retcode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
