import re
from typing import Dict, List, Optional
from solitude import hookimpl


def match_csubmit_command_str(cmd: str) -> Optional[re.Match]:
    return re.search(
        r"c-submit\s+(?:(?:--\S+(?:\s*[=\s]\s*\S+)?\s+)*)?(?P<user>\S+)"
        r"\s+(?P<ticket>\S+)\s+(?P<duration>\d+)\s+(?P<image>\D\S+)\s*(?P<args>.*)",
        cmd.strip(),
    )


def filter_csubmit_command_str(cmd: str) -> str:
    result = match_csubmit_command_str(cmd=cmd)
    assert result is not None
    return (
        result.groupdict()["image"] + " " + result.groupdict()["args"]
    ).strip()


@hookimpl
def matches_command(cmd: str) -> bool:
    return match_csubmit_command_str(cmd=cmd) is not None


@hookimpl
def get_command_hash(cmd: str) -> str:
    return filter_csubmit_command_str(cmd=cmd)


@hookimpl
def retrieve_state(cmd: str) -> Dict:
    return {}


@hookimpl
def is_command_job_done(cmd: str, state: Dict) -> bool:
    return False


@hookimpl
def get_command_status_str(cmd: str, state: Dict) -> str:
    return filter_csubmit_command_str(cmd=cmd)


@hookimpl
def get_errors_from_log(log: str) -> List[str]:
    errors = []
    if log.find("Killed") != -1:
        errors.append("NoResource")
    if log.find("CUDA_ERROR") != -1:
        errors.append("CUDA")
    errors = errors + [e[1:-1] for e in re.findall(r"\s.*Error:", log)]
    return errors
