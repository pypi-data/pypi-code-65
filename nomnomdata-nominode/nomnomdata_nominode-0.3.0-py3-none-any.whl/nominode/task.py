import json
import logging
from typing import Any, Dict, List, Optional, Union

import click
from mergedeep import Strategy, merge

from nomnomdata.auth.auth import NominodeAuth

from .util import (
    NominodeSession,
    create_nested_dic,
    exclude_keys,
    get_nested_value,
    load_config,
    masked_copy,
    omit_copy,
    rblob,
)

_logger = logging.getLogger(__name__)
SYSTEM_FIELDS = [
    "versions",
    "updated",
    "engine",
    "concurrency",
    "engine_alias",
    "last_execution",
    "last_execution_uuid",
    "last_successful_execution_uuid",
    "created",
    "actions",
    "notify",
    "status",
    "_deploy",
]


def create_session(nominode_url):
    """
    :param nominode_url: url of the nominode you are attempting to hit
    :return: requests session
    """
    session = NominodeSession(prefix_url=nominode_url)
    session.auth = NominodeAuth()
    return session


def parse_config(string, file):
    assert (
        string or file
    ), "A task config must be provided as either a json string, or a path for a file containing a json string."

    if string:
        config = json.loads(string)
    else:
        config = file

    assert config.get("project_uuid"), "project identifier must be specified"
    assert config.get("uuid"), "task_uuid must be specified"
    return config


def _exists(nominode, task_uuid, project_uuid, detailed=False) -> Union[bool, dict, list]:
    """

    :param nominode:
    :param task_uuid:
    :param project_uuid:
    :return: bool|dict|list
    """
    session = create_session(nominode_url=nominode)
    response = session.get(url=f"""/api/v2/projects/{project_uuid}/tasks/{task_uuid}""",)

    if detailed and response.ok:
        return omit_copy(response.json(), ["engine", "engine_alias"])

    # some other error. maybe worth a log
    if not response.ok and response.status_code != 404:
        _logger.debug(response.text)

    return response.ok


def _filter(results_text):
    results = json.loads(results_text)
    results.pop("engine", None)
    results.pop("engine_alias", None)
    return results


@click.group(name="task")
def task():
    pass


@task.command(name="create")
@click.option(
    "-n",
    "--nominode",
    help="Specify the url of the Nominode you are connecting to.",
    envvar="NOMINODE_URL",  # NOMINODE_URL=https://staging.web.nomnomdata.com/api/v2/
)
@click.option(
    "-s",
    "--string",
    help="String of the JSON of the task you want to update.",
    required=False,
)
@click.option(
    "-f",
    "--file",
    help="Path to the file containing JSON config of the task you want to update.",
    callback=load_config,
    required=False,
)
@click.option(
    "--overwrite",
    help="If true will overwrite any pre-existing task with new values",
    is_flag=True,
)
@click.pass_context
def create(ctx, nominode, string, file, overwrite):
    """
    Create a new task on a nominode.  Will fail if uuid, or specified task alias already exists
    """
    task_config = parse_config(string, file)
    assert task_config.get(
        "engine_uuid"
    ), "engine_uuid must be specified to create a task"

    exists = _exists(
        nominode=nominode,
        task_uuid=task_config["uuid"],
        project_uuid=task_config["project_uuid"],
    )

    if overwrite or not exists:
        session = create_session(nominode_url=nominode)
        response = session.put(
            url=f"""/api/v2/projects/{task_config["project_uuid"]}/tasks/{task_config["uuid"]}""",
            json=task_config,
        )
        response = rblob(
            code=response.status_code,
            status="Success",
            message="",
            results=_filter(response.text),
        )

    else:
        response = rblob(code=400, status="Failure", message="Task already exists.",)

    click.echo(response)
    return response


@task.command(name="delete")
@click.option(
    "-n",
    "--nominode",
    help="Specify the url of the Nominode you are connecting to.",
    envvar="NOMINODE_URL",  # NOMINODE_URL=https://staging.web.nomnomdata.com/api/v2/
)
@click.option(
    "-pu",
    "--project-uuid",
    help="String of the UUID of the project where your task lives",
    envvar="PROJECT_UUID",
)
@click.option(
    "-tu", "--task-uuid", help="String of the UUID of the task you want to delete",
)
def delete(
    nominode, task_uuid, project_uuid,
):
    """
    Update an existing task on a nominode.
    Will fail if task does not exits or not found via uuid
    """
    session = create_session(nominode_url=nominode)
    response = session.delete(
        url=f"""/api/v2/projects/{project_uuid}/tasks/{task_uuid}""",
    )

    if response.status_code == 404:
        response = rblob(
            status="Not Found",
            code=response.status_code,
            message=f"Unable to locate task identified by uuid: {task_uuid}",
            results={},
        )

    elif not response.ok:
        response = rblob(
            status="Failure",
            code=response.status_code,
            message=f"Unable to delete task identified by uuid: {task_uuid}",
            results={},
        )

    else:
        response = rblob(
            results=[],
            status="Success",
            code=response.status_code,
            message=f"Task identified by uuid: {task_uuid} successfully deleted",
        )

    click.echo(response)
    return response


@task.command(name="get")
@click.option(
    "-n",
    "--nominode",
    help="Specify the url of the Nominode you are connecting to.",
    envvar="NOMINODE_URL",  # NOMINODE_URL=https://staging.web.nomnomdata.com/api/v2/
)
@click.option(
    "-pu",
    "--project-uuid",
    help="String of the UUID of the project where your task lives",
    envvar="PROJECT_UUID",
)
@click.option(
    "-tu", "--task-uuid", help="String of the UUID of the task you want to retrieve",
)
def get(nominode, task_uuid, project_uuid):
    """

    :param nominode:
    :param task_uuid:
    :param project_uuid:
    :return:
    """
    session = create_session(nominode_url=nominode)
    response = session.get(url=f"""/api/v2/projects/{project_uuid}/tasks/{task_uuid}""",)

    payload = response.json()

    if response.status_code == 404:
        response = rblob(
            status="Not Found",
            code=response.status_code,
            message=payload.get("message"),
            results={},
        )

    elif not response.ok:
        response = rblob(
            status="Failure",
            code=response.status_code,
            message=payload.get("message"),
            results={},
        )
    else:
        response = rblob(
            status="Success",
            code=response.status_code,
            message=payload.get("message"),
            results=omit_copy(payload, ["engine", "engine_alias"]),
        )

    click.echo(response)
    return response


@task.command(name="update")
@click.option(
    "-n",
    "--nominode",
    help="Specify the url of the Nominode you are connecting to.",
    envvar="NOMINODE_URL",  # NOMINODE_URL=https://staging.web.nomnomdata.com/api/v2/
)
@click.option(
    "-s",
    "--string",
    help="String of the JSON of the task you want to update.",
    required=False,
)
@click.option(
    "-f",
    "--file",
    help="Path to the file containing JSON config of the task you want to update.",
    callback=load_config,
    required=False,
)
@click.option("--dry-run", is_flag=True, help="Pretend to perform said action")
def update(
    nominode, string, file, dry_run=False,
):
    """

    :param nominode:
    :param task_config:
        Sample File Contents
        {
          "_deploy": {"exclude": ["parameters.seconds", "options"]},
          "alias": "Junk Test",
          "engine_uuid": "df6872b9-e8bd-11ea-acb4-0e89e1759f15",
          "project_uuid": "{{ @tests/sample/project.json|project_uuid }}",
          "options": {"channel": "stable"},
          "uuid": "{{ @tests/sample/task1_uuid.txt }}",
          "parameters": {
              "action_name": "wait_seconds",
              "alias": "Junk Test",
              "seconds": 30
          }
        }
    :param fields_to_update:
    :param dry_run:
    :return:
    """

    input_data = parse_config(string, file)

    session = create_session(nominode_url=nominode)
    existing_task = _exists(
        nominode=nominode,
        task_uuid=input_data["uuid"],
        project_uuid=input_data["project_uuid"],
        detailed=True,
    )
    if not existing_task:
        return rblob(
            code=404,
            status="Not Found",
            message=f"""Unable to locate task `{input_data['uuid']}`""",
            results={},
        )
    to_update = {}
    to_exclude = []
    final = {}

    # Grab values from task_config that are explicitly specified to be included or excluded
    deploy = input_data.get("_deploy")
    if deploy and "exclude" in deploy:
        input_data.pop("_deploy", None)
        to_update = exclude_keys(deploy["exclude"], input_data or {})

    merge(
        final, existing_task, to_update or input_data, strategy=Strategy.TYPESAFE_REPLACE
    )

    # Exclude system fields must happen at the end otherwise
    # excluded fields specified in parameters might be deleted from the existing task
    for key in SYSTEM_FIELDS:
        final.pop(key, None)
        existing_task.pop(key, None)

    if existing_task == final:
        response = rblob(
            code=200, status="Success", message="No change detected", results=final,
        )
    elif not dry_run:
        response = session.put(
            url=f"""/api/v2/projects/{input_data["project_uuid"]}/tasks/{input_data["uuid"]}""",
            json=final,
        )

        payload = response.json()

        if response.ok:
            response = rblob(
                code=response.status_code,
                status="Success",
                message=payload.get("message"),
                results=omit_copy(payload, ["engine", "engine_alias"]),
            )
        else:
            response = rblob(
                code=response.status_code,
                status="Failure",
                message=payload.get("message"),
                results=payload.get("errors") or payload,
            )
    else:
        response = rblob(
            code=202,
            status="Dry Run",
            message="Pretended to update to the following result",
            results=final,
        )

    click.echo(response)
    return response
