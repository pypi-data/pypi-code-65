from copy import deepcopy
from functools import partial
import json
import os
from typing import Any, Callable, Dict, MutableMapping, Optional

import click
import wrapt

from anyscale.project import get_project_id
from anyscale.util import get_working_dir, send_json_request


@wrapt.decorator  # type: ignore
def _with_safe_cluster_config(
    wrapped: Callable[..., MutableMapping[str, Any]],
    instance: Optional[Any],
    args: Any,
    kwargs: Any,
) -> Any:
    # for all our _configure_* functions, the first argument should be the cluster config
    def _configure(
        cluster_config: MutableMapping[str, Any], *args: Any, **kwargs: Any
    ) -> MutableMapping[str, Any]:
        cluster_config = deepcopy(cluster_config)

        return wrapped(cluster_config, *args, **kwargs)

    return _configure(*args, **kwargs)


@_with_safe_cluster_config  # type: ignore
def _configure_cluster_name(
    cluster_config: MutableMapping[str, Any], session_id: str
) -> MutableMapping[str, Any]:
    details = send_json_request("/api/v2/sessions/{}/details".format(session_id), {})[
        "result"
    ]

    cluster_config["cluster_name"] = details["cluster_name"]

    return cluster_config


@_with_safe_cluster_config  # type: ignore
def _configure_ssh_key(
    cluster_config: MutableMapping[str, Any], session_id: str,
) -> MutableMapping[str, Any]:
    ssh_key = send_json_request("/api/v2/sessions/{}/ssh_key".format(session_id), {})[
        "result"
    ]

    # TODO (yiran): cleanup SSH keys if session no longer exists.
    def _write_ssh_key(name: str, ssh_key: str) -> str:
        key_path = os.path.join(os.path.expanduser("~/.ssh"), "{}.pem".format(name))
        os.makedirs(os.path.dirname(key_path), exist_ok=True)

        with open(key_path, "w", opener=partial(os.open, mode=0o600)) as f:
            f.write(ssh_key)

        return key_path

    key_path = _write_ssh_key(ssh_key["key_name"], ssh_key["private_key"])

    cluster_config.setdefault("auth", {})["ssh_private_key"] = key_path

    # Bypass Ray's check for cloudinit key
    cluster_config["head_node"].setdefault(("UserData"), "")
    cluster_config["worker_nodes"].setdefault(("UserData"), "")
    return cluster_config


@_with_safe_cluster_config  # type: ignore
def _configure_autoscaler_credentials(
    cluster_config: MutableMapping[str, Any], session_id: str
) -> MutableMapping[str, Any]:
    credentials = send_json_request(
        "/api/v2/sessions/{}/autoscaler_credentials".format(session_id), {},
    )["result"]

    cloud_provider = cluster_config["provider"]["type"]
    cluster_config["provider"]["{}_credentials".format(cloud_provider)] = credentials[
        "credentials"
    ]

    return cluster_config


@_with_safe_cluster_config  # type: ignore
def _update_file_mounts(
    cluster_config: Dict[str, Any], project_root_dir: str
) -> Dict[str, Any]:
    project_id = get_project_id(project_root_dir)
    working_dir = get_working_dir(cluster_config, project_id)
    for remote_path, local_path in cluster_config.get("file_mounts", {}).items():
        if remote_path == working_dir and not os.path.samefile(
            local_path, project_root_dir
        ):
            click.confirm(
                '"{remote}: {local}" has been detected in the file mounts.\n'
                'Anyscale needs to sync the local project directory "{proj}" '
                'with "{remote}" in the cluster.\nCan this file mount be replaced for '
                "this command?\nThis action will not change your session "
                "configuration file.".format(
                    remote=remote_path, local=local_path, proj=project_root_dir,
                ),
                abort=True,
            )
    cluster_config["file_mounts"].update({working_dir: project_root_dir})
    return cluster_config


def configure_for_session(
    session_id: str,
    project_root_dir: str,
    _DO_NOT_USE_RAY_UP_ONLY_cluster_config: Optional[  # noqa: N803
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    cluster_config: Dict[str, Any] = {}
    if _DO_NOT_USE_RAY_UP_ONLY_cluster_config is not None:
        cluster_config = _DO_NOT_USE_RAY_UP_ONLY_cluster_config
    else:
        _resp: Dict[str, Any] = send_json_request(
            "/api/v2/sessions/{}/cluster_config".format(session_id), {}
        )["result"]
        cluster_config = json.loads(_resp["config_with_defaults"])
        cluster_config = _configure_cluster_name(cluster_config, session_id)

    cluster_config = _configure_ssh_key(cluster_config, session_id)
    cluster_config = _configure_autoscaler_credentials(cluster_config, session_id)
    cluster_config = _update_file_mounts(cluster_config, project_root_dir)

    return cluster_config
