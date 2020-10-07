import argparse
import json
import logging
import os
from sys import stderr
from collections import namedtuple
from time import sleep, time
from typing import Iterable, Optional

import requests

_tfe_api_token = os.getenv("TFE_API_TOKEN")

Run = namedtuple("Run", ["run", "ingress_attributes"])


def _get(path: str, params: dict = {}) -> Optional[dict]:
    hdrs = {"Authorization": f"Bearer {_tfe_api_token}"}

    if path.startswith("/api/") or path.startswith("api/"):
        url = f'https://app.terraform.io/{path.lstrip("/")}'
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    r = requests.get(url, headers=hdrs, params=params)
    if r.status_code == 200:
        return r.json()["data"]
    elif r.status_code == 404:
        return None
    else:
        raise Exception(f"failed to get {path}, status code {r.status_code}, {r.text}")


def _list(path: str, headers: dict = {}, params: dict = {}) -> Iterable[dict]:
    prms = {"page[size]": 15}
    hdrs = {"Authorization": f"Bearer {_tfe_api_token}"}
    if headers:
        hdrs.update(headers)
    if params:
        prms.update(params)

    if path.startswith("api/"):
        url = f"https://app.terraform.io/{path}"
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    r = requests.get(url, headers=hdrs, params=prms)
    while r.status_code == 200:
        response = r.json()
        next_page = response.get("links", {}).get("next")
        for d in response["data"]:
            yield d

        if next_page:
            r = requests.get(next_page, headers=hdrs)
        else:
            return

    if r.status_code not in (200, 404):
        raise Exception(f"failed to list {path}, status code {r.status_code}, {r.text}")


def find_run_for_commit(workspace: dict, url: str, commit_sha: str) -> Optional[Run]:
    for run in _list(f'workspaces/{workspace["id"]}/runs'):
        configuration_version_id = (
            run.get("relationships", {})
            .get("configuration-version", {})
            .get("data", {})
            .get("id")
        )
        if configuration_version_id:
            ingress_attributes = _get(
                f"configuration-versions/{configuration_version_id}/ingress-attributes"
            )
            if ingress_attributes:
                ia_clone_url = ingress_attributes.get("attributes", {}).get("clone-url")
                ia_commit_sha = ingress_attributes.get("attributes", {}).get(
                    "commit-sha"
                )
                if ia_clone_url == url and ia_commit_sha == commit_sha:
                    return Run(run, ingress_attributes)

    return None


def get_apply(run: dict) -> Optional[dict]:
    apply_link = (
        run.get("relationships", {}).get("apply", {}).get("links", {}).get("related")
    )
    return _get(apply_link)


def get_plan(run: dict) -> Optional[dict]:
    plan_id = (
        run.get("relationships", {}).get("plan", {}).get("links", {}).get("related")
    )
    return _get(plan_id)


def wait_until(
    workspace: dict,
    wait_for_status: str,
    clone_url: str,
    commit_sha: str,
    maximum_wait_time_in_seconds: int,
    verbose: bool = False,
):
    workspace_name = workspace["attributes"]["name"]
    now = start_time = time()
    while (now - start_time) < maximum_wait_time_in_seconds:
        run = find_run_for_commit(workspace, clone_url, commit_sha)
        if run:
            if verbose:
                logging.info("%s\n", json.dumps(run, indent=2))

            run_id = run.run["id"]
            status = run.run.get("attributes").get("status")
            if status == wait_for_status:
                logging.info(
                    "run %s in workspace %s has reached state %s",
                    run_id,
                    workspace_name,
                    wait_for_status,
                )
                return 0
            elif status in (
                "discarded",
                "errored",
                "canceled",
                "force_canceled",
                "planned_and_finished",
            ):
                logging.error(
                    "run %s in workspace %s has status %s and can no longer reach the desired status of %s",
                    run_id,
                    workspace_name,
                    status,
                    wait_for_status,
                )
                return 1
            else:
                logging.info(
                    "run %s in workspace %s has status %s, waiting 60s",
                    run_id,
                    workspace_name,
                    status,
                )
                stderr.flush()
                sleep(60)
        else:
            logging.info(
                "waiting for a run in workspace %s for commit %s in %s to appear",
                workspace_name,
                commit_sha[0:7],
                clone_url,
            )
            stderr.flush()
            sleep(60)
        now = time()

    logging.error(
        "time out while waiting for a run in workspace %s to reach  state %s",
        run_id,
        workspace_name,
        wait_for_status,
    )


class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser(
        description="wait for TFE run to reach specified state."
    )
    parser.add_argument(
        "--token",
        action=EnvDefault,
        envvar="TFE_API_TOKEN",
        help="Terraform Enterprise access token, default from TFE_API_TOKEN",
    )

    parser.add_argument("--organization", required=True, help="of the workspace")
    parser.add_argument("--workspace", required=True, help="to inspect runs for")
    parser.add_argument(
        "--clone-url", required=True, help="of source repository for the run"
    )
    parser.add_argument(
        "--commit-sha", required=True, help="of commit which initiated the run"
    )
    parser.add_argument(
        "--wait-for-status",
        required=False,
        default="planned_and_finished",
        help="wait state to reach",
    )
    parser.add_argument(
        "--maximum-wait-time",
        required=False,
        type=int,
        default=45 * 60,
        help="for state to be reached in minutes, default 45",
    )
    parser.add_argument(
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="show verbose output",
    )
    args = parser.parse_args()

    global _tfe_api_token
    _tfe_api_token = args.token

    org = _get(f"organizations/{args.organization}")
    if not org:
        parser.error(f"unknown organization {args.organization}.")

    workspace = _get(f"organizations/{args.organization}/workspaces/{args.workspace}")
    if not workspace:
        parser.error(
            f"workspace {args.workspace} is unknown in organization {args.organization}."
        )

    exit(
        wait_until(
            workspace,
            args.wait_for_status,
            args.clone_url,
            args.commit_sha,
            args.maximum_wait_time * 60,
            args.verbose,
        )
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"), format="%(levelname)s: %(message)s"
    )
    main()
