import json
from typing import Union

import kingghidorah as kd
from kingghidorah.calls import _APIRequest
from kingghidorah.sanitizers import _url_sanitizer
from kingghidorah.utils import _check_index


@_check_index
def GetAllProjects() -> list:
  """Get's all projects available for the current user and returns a list.

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- name

            \t-- description

            \t-- creator

            \t-- admins

            \t-- workers

            \t-- created

            \t-- updated

            \t-- workflow_count

            \t-- resource_count

            \t-- resourcelist_count

            \t-- url

            \t-- uui

            **These properties can be used to search for a specific project or a group of projects.**
	"""
  # return _APIRequest().get(f"/projects/?name__icontains={name}")["results"]
  return _APIRequest().get("/projects")["results"]


@_check_index
def GetAllWorkflows() -> list:
  """Get's all Workflows available for the current user and returns a list.

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- name

            \t-- description

            \t-- creator

            \t-- created

            \t-- url

            \t-- uuid

            \t-- project

            \t-- valid

            \t-- updated

            **These properties can be used to search for a workflow or a group of workflows.**
	"""
  # return _APIRequest().get(f"/workflows/?name__icontains={name}")["results"]
  return _APIRequest().get("/workflows")["results"]


@_check_index
def GetAllResourceTypes() -> list:
  """Get's all ResourceTypes available for Rodan returns a list.

    When a job is loaded into Rodan, resource types that are used in the rodan job are defined in a yaml file (resource_types.yml).

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- url

            \t-- uuid

            \t-- mimetype

            \t-- extension

            \t-- description

            **These properties can be used to search for a specific resourcetype.**
	"""
  # if name is not None:
  #   return _APIRequest().get(f"/resourcetypes/?mimetype__icontains={name}&format=json")["results"]
  # else:
  return _APIRequest().get("/resourcetypes")["results"]


@_check_index
def GetAllResources() -> list:
  """Get's all Resources from all projects

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- name

            \t-- description

            \t-- url

            \t-- uuid

            \t-- creator

            \t-- created

            \t-- updated

            \t-- project

            \t-- resource_type

            \t-- resource_file

            \t-- viewer_url

            \t-- error_details

            \t-- origin

            **These properties can be used to search for a specific resources.**
	"""
  # return _APIRequest().get(f"/resources/?name__icontains={name}&format=json")["results"]
  return _APIRequest().get("/resources")["results"]


@_check_index
def GetAllInputs() -> list:
  """Get's all inputs from all projects

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- url

            \t-- uuid

            \t-- Text output

            \t-- output_port_type

            \t-- output_port_type_name

            \t-- run_job

            \t-- resource

            **These properties can be used to search for a specific inputs.**
	"""
  return _APIRequest().get("/inputs")["results"]


@_check_index
def GetAllOutputs() -> list:
  """Get's all outputs from all projects

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- url

            \t-- uuid

            \t-- Text output

            \t-- output_port_type

            \t-- output_port_type_name

            \t-- run_job

            \t-- resource

            **These properties can be used to search for a specific outputs.**
	"""
  return _APIRequest().get("/outputs")["results"]


@_check_index
def GetAllJobs() -> list:
  """Get's all jobs from all projects

    :return: Returns a list of Objects that have the following properties.
    :rtype: List

    These properties exist for every object in the list.

            \t-- url

            \t-- uuid

            \t-- name

            \t-- settings

            \t-- description

            \t-- input_port_types

                    \t\t-- **[** url **]** (list of URLS)

            \t-- output_port_types

                            \t\t-- **[** url **]** (list of URLS)

            \t-- category

            \t-- enabled

            \t-- interacive
	"""
  return _APIRequest().get("/jobs")["results"]


def GetProject(uuid) -> dict:
  """Retrive a project by UUID

    :param [uuid]: A string of the UUID for a specific Rodan Project
    :type [uuid]: String

    :return: A project object with the following properties.
    :rtype: JSON

            \t-- url

            \t-- name

            \t-- description

            \t-- creator

            \t-- workflows

                    \t **[**

                    \t\t-- url

                    \t\t-- name

                    \t **]**

            \t-- resources

                    \t **[**

                    \t\t-- url

                    \t\t-- name

                    \t **]**

            \t-- resourcelists

            \t-- created

            \t-- updated

            \t-- admins

            \t-- workers

            \t-- admins_url

            \t-- workers_url

            You can retrieve all sorts of information from this entry point.
	"""
  return _APIRequest().get("/project/" + uuid)


def GetWorkflow(uuid=None) -> dict:
  """Retrive a workflow by UUID

    :param [uuid]: A string of the UUID to search for.
    :type [uuid]: String

    :return: A project object with the following properties.
    :rtype: JSON

            \t-- url

            \t-- uuid

            \t-- name

            \t-- project

            \t-- workflow_jobs

                    \t **[**

                    \t\t-- url

                    \t\t-- uuid

                    \t\t-- workflow

                    \t\t-- input_ports

                            \t\t **[**

                            \t\t\t-- url

                            \t\t\t-- uuid

                            \t\t\t-- input_port_type

                            \t\t\t-- label

                            \t\t\t-- extern

                            \t\t\t-- workflow_job

                            \t\t\t-- connections

                            \t\t **]**

                    \t\t-- output_ports

                            \t\t **[**

                            \t\t\t-- url

                            \t\t\t-- uuid

                            \t\t\t-- output_port_type

                            \t\t\t-- label

                            \t\t\t-- extern

                            \t\t\t-- workflow_job

                            \t\t\t-- connections

                            \t\t **]**

                    \t\t-- job_name

                    \t\t-- job_description

                    \t\t-- job

                    \t\t-- job_settings

                    \t\t-- name

                    \t\t-- group

                    \t\t-- created

                    \t\t-- updated

                    \t **]**

            \t-- description

            \t-- created

            \t-- updated

            \t-- creator

            \t-- valid

            **This object is very verbose**

	"""
  if uuid:
    pass
  else:
    uuid = [i for i in url.split("/") if len(i) == 36][0]

  return _APIRequest().get("/workflow/" + uuid)


def GetResource(uuid: str) -> dict:
  """Retrive a resource by UUID

    :param [uuid]: The UUID of a resource.
    :type [uuid]: String

    :return: This will return a JSON object with the following keys.
    :rtype: JSON

            \t-- url

            \t-- uuid

            \t-- creator

            \t-- resource_file

            \t-- viewer_url

            \t-- name

            \t-- description

            \t-- processing_status

            \t-- error_summary

            \t-- error_details

            \t-- created

            \t-- updated

            \t-- project

            \t-- resource_type

            \t-- origin

            **You can download resources this way**
	"""
  return _APIRequest().get("/resource/" + uuid)


def CreateProject(name: str) -> dict:
  """Creates a project for the logged in user.

    :param [name]: The name to give to a new project
    :type [name]: String

    :return: JSON dictionary of the project
    :rtype: JSON
	"""
  call = _APIRequest()
  data = {
    "name": name,
    "creator": {
      "username": call.username
    },
    "created": None,
    "updated": None,
    "workflow_count": None,
    "resource_count": None,
  }
  return _APIRequest().post("/projects", data)


def CreateWorkflow(name: str, project: str, json_workflow=[]) -> dict:
  """Create a workflow

    :param [name]: The name you wish to give to the workflow.
    :type [name]: String

    :param [project]: The project (UUID) you wish to place the workflow in.
    :type [project]: String

    :param [json_workflow]: A filepath for the exported json workflow from Rodan.
    :type [json_workflow]: String

    :return: JSON of the created workflow
    :rtype: JSON
	"""
  call = _APIRequest()
  data = {
    "name": name,
    "description": None,
    "created": None,
    "updated": None,
    "valid": False,
    "project": call.domain + "project/" + _url_sanitizer(project),
    "connections": [],
    "workflow_input_ports": [],
    "workflow_output_ports": [],
    "workflow_jobs": [],
    "workflow_runs": [],
  }

  # abusing str = true and list = false, this might break
  if json_workflow:
    with open(json_workflow) as f:
      workflow_data = {"serialized": json.loads(f.read())}

    workflow_data["serialized"]["name"] = name
    data = {**data, **workflow_data}

  req = call.post("/workflows", json=data)
  # TODO: Update the connect ports automatically that don't already have an input
  # 	AKA->populating extern=True 's

  if "serialized" in req:
    raise Exception(f"Job not installed in Rodan: {req}")

  # Trigger valid workflow check
  # TODO: Review where the check happens
  call.patch("/workflow/" + req["uuid"], data={"valid": True})
  return req


def RunWorkflow(name: str, workflow: str, resource_assignments: dict={}, description: str = []) -> dict:
  """Run a specific workflow

    :param [name]: The name to give to the workflow.
    :type [name]: String

    :param [workflow]: The UUID for a currently uploaded workflow you wish to run.
    :type [workflow]: String

    :param [resource_assignment]: A list of tuples(3) assigning specific resource UUIDs to specific job ports. For example:
    :type [resource_assignment]: List
	"""
  call = _APIRequest()
  if not description:
    description = f"Run of Workflow '{name}'"

  data = {
    "name": name,
    "description": description,
    "workflow": call.domain + "workflow/" + _url_sanitizer(workflow),
    "resource_assignments": resource_assignments,
    "created": None,
    "updated": None,
    "statusText": "Unknown status",
  }
  print(data["workflow"])
  return call.post("/workflowruns", json=data)


def UploadFile(name: Union[str, list], mime_type: str, project: str, description: str="") -> Union[str, list]:
  """Upload a file to Rodan

    :param [name]: A filepath to the file you wish to upload
    :type [name]: String

    :param [mime_type]: A resource type UUID that identifies the filetype.
    :type [mime_type]: String

    :param [project]: A project UUID that identifies the project in which to upload a resource to.
    :type [project]: String

    :param [description]: A description of the file.
    :type [description]: String (optional)

	"""
  call = _APIRequest()

  if isinstance(name, str):
    names = [name]
  elif isinstance(name, list):
    names = name
  else:
    raise TypeError(f"Type: {type(name)} is not supported.")

  data = []
  for name in names:
    f = call.post(
      "/resources",
      data={
        "project": call.domain + "project/" + _url_sanitizer(project),
        "type": call.domain + "resourcetype/" + _url_sanitizer(mime_type),
      },
      files={
        "files": open(name, "rb"),
      },
    )[0]
    data.append(f)

  if len(data) == 1:
    return data[0]
  else:
    return data


def ModifyFile(uuid: str, name: str=None, description: str=None, resource_type: str=None, labels: str=None) -> dict:
  """
	Modify File uploaded
  """
  call = _APIRequest()

  data = {}
  if name is not None:
    data["name"] = name
  if description is not None:
    data["description"] = description
  if resource_type is not None:
    data["resource_type"] = resource_type
  if labels is not None:
    data["labels"] = labels

  f = call.patch("/resource/" + uuid, data=data)
  return f


def DeleteProject(uuid: str):
  """Delete a project from existance on Rodan.

    **This will also delete all resources, workflow, runjobs, etc. associated with this project.
    You have been warned.**


    :param [uuid]: A UUID of the project you want to delete.
    :type [uuid]: String

    :return: Information about the deleted project.
    :rtype: JSON in the same structure as :func:`kingghidorah.GetProject`.
	"""
  call = _APIRequest()

  try:
    call.delete("project/" + uuid)
  except kd.exceptions._Error:
    raise Exception("Deleting project failed.")

  return {"status": f"Project {uuid} deleted"}


def DeleteWorkflow(uuid: str) -> dict:
  """Delete a workflow from Rodan.

    :param [uuid]: A UUID of the workflow you want to delete.
    :type [uuid]: String

    :return: Information about the deleted workflow.
    :rtype: JSON in the same structure as :func:`kingghidorah.GetWorkflow`.
	"""
  call = _APIRequest()

  try:
    call.delete("workflow/" + uuid)
  except kd.exceptions._Error:
    raise Exception("Deleting workflow failed.")

  return {"status": f"Workflow {uuid} deleted"}


def DeleteFile(uuid: str, force=False) -> dict:
  """Delete a file from Rodan

    As with most API points sent a DELETE method to rodan, it doesn't reply with anything (which it should),

    :param [uuid]: The UUID of the file you want to delete.
    :type [uuid]: String

    :return: Information about the deleted file.
    :rtype: JSON in the same strucutre as :func:`kingghidorah.GetResource`.
	"""
  call = _APIRequest()

  try:
    call.delete("resource/" + uuid)
  except kd.exceptions._Error:
    raise Exception("Deleting resource failed.")

  return {"status": f"Resource {uuid} deleted"}


def GetWorkflowJob(uuid: str) -> dict:
  """
  """
  call = _APIRequest()
  return call.get("workflowjob/" + uuid)


def ModifyWorkflowJob(uuid,
                      appearance=None,
                      job_settings=None,
                      input_ports=None,
                      output_ports=None):
  """
	"""
  call = _APIRequest()
  data = {}
  import json

  if appearance is not None:
    data["appearance"] = appearance
  if job_settings is not None:
    data["job_settings"] = job_settings
  if input_ports is not None:
    data["input_ports"] = input_ports
  if output_ports is not None:
    data["output_ports"] = output_ports

  return call.patch("workflowjob/" + uuid, json=data)
