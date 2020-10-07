import argparse
import logging
import os
from time import sleep, time
from typing import Iterable, Optional
from tfe_run_wait.env_default import EnvDefault

import requests

_tfe_api_token = os.getenv("TFE_API_TOKEN")


def _get(path: str, params: dict = {}) -> Optional[dict]:
    hdrs = {"Authorization": f"Bearer {_tfe_api_token}"}

    if path.startswith("/api/") or path.startswith("api/"):
        url = f'https://app.terraform.io/{path.lstrip("/")}'
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    logging.debug("get %s, %s", url, params)
    r = requests.get(url, headers=hdrs, params=params)
    if r.status_code == 200:
        return r.json()["data"]
    elif r.status_code == 404:
        return None
    else:
        raise Exception(f"failed to get {path}, status code {r.status_code}, {r.text}")


def _list(path: str, headers: dict = {}, params: dict = {}) -> Iterable[dict]:
    prms = {"page[size]": 100}
    hdrs = {"Authorization": f"Bearer {_tfe_api_token}"}
    if headers:
        hdrs.update(headers)
    if params:
        prms.update(params)

    if path.startswith("api/"):
        url = f"https://app.terraform.io/{path}"
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    logging.debug("get %s, %s", url, params)
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



def find_run_for_commit(workspace: dict, url: str, commit_sha: str) -> Optional[dict]:
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
                    return run
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
):
    run_id = None
    workspace_name = workspace["attributes"]["name"]
    now = start_time = time()
    while (now - start_time) < maximum_wait_time_in_seconds:
        if not run_id:
            run = find_run_for_commit(workspace, clone_url, commit_sha)
        else:
            run = _get(f"/api/v2/runs/{run_id}")

        if run:
            run_id = run["id"]
            status = run.get("attributes").get("status")
            if status == wait_for_status:
                logging.info(
                    "%s in workspace %s has reached state %s",
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
                    "%s in workspace %s has status %s and can no longer reach the desired status of %s",
                    run_id,
                    workspace_name,
                    status,
                    wait_for_status,
                )
                return 1
            else:
                logging.info(
                    "%s in workspace %s in status %s, waited %ss",
                    run_id,
                    workspace_name,
                    status,
                    int(time() - start_time)
                )
                sleep(10)
        else:
            logging.info(
                "waiting %ss for a run in workspace %s for commit %s in %s to appear",
                int(time() - start_time),
                workspace_name,
                commit_sha[0:7],
                clone_url,
            )
            sleep(10)
        now = time()

    if run_id:
        logging.error(
            "timed out after %ss waiting for %s in workspace %s to reach state %s",
            int(time() - start_time),
            run_id,
            workspace_name,
            wait_for_status,
        )
    else:
        logging.error(
            "time out while waiting for a run in workspace %s for commit %s in %s to appear",
            run_id,
            workspace_name,
            commit_sha[0:7],
            clone_url,
        )
    return 1


def _wait():
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

    logging.info(f"waiting for run in {args.organization}:{args.workspace} for commit {args.commit_sha[0:7]} in repository {args.clone_url}")
    exit(
        wait_until(
            workspace,
            args.wait_for_status,
            args.clone_url,
            args.commit_sha,
            args.maximum_wait_time * 60,
        )
    )

def main():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(levelname)s: %(message)s",
    )
    _wait()

if __name__ == "__main__":
    main()
