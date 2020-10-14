from contextlib import contextmanager
from functools import wraps
import random
import string
from uuid import UUID

import kingghidorah as kd
from kingghidorah.exceptions import _NoMoreResources


def _check_index(func):

  @wraps(func)
  def wrapper(*args, **kwargs):
    data = func(*args, **kwargs)
    try:
      data[-1]
    except IndexError:
      raise _NoMoreResources()
    return data

  return wrapper


def extract_uuid(url: str) -> str:
  """
    Return the UUID from a url
    """
  for i in url.split("/"):
    try:
      obj = UUID(i, version=4)
      return i
    except ValueError:
      pass


def assemble_resource_assignments(workflow: dict,
                                  port_assignment: list,
                                  resource_assignments: dict = {}) -> dict:
  """
	workflow              -> is retrieved using kd.GetWorkflow
	port_assignment       -> is a list of tuples (job_name, port_name, [uploaded_file_uuid])
	resource_assignments  -> start with an empty dict.
	"""
  for workflow_job in workflow["workflow_jobs"]:
    for input_port in workflow_job["input_ports"]:
      if not input_port["connections"]:
        for triple in port_assignment:
          if (workflow_job["job_name"] == triple[0] and input_port["label"] == triple[1]):
            resource_assignments[input_port["url"]] = triple[2]
            break

  return resource_assignments


def random_gen():
  return "".join(random.SystemRandom().choice(
    # a-z and A-Z
    string.ascii_letters + string.digits  # 0-9
    + string.punctuation  # !@#$...
  ) for _ in range(50))


@contextmanager
def create_project(*args, **kwds):

  try:
    n = kwds["name"]
  except NameError:
    n = random_gen()

  tmp = kd.CreateProject(name=n)
  try:
    yield tmp
  finally:
    kd.DeleteProject(uuid=tmp["uuid"])


@contextmanager
def create_resource(*args, **kwargs):

  try:
    p = kwargs["project"]
    n = kwargs["name"]
    t = kwargs["mime_type"]
  except NameError:
    raise Exception(
      "Missing parameter (either project, filename, mimetype, or any combination.)")

  tmp = kd.UploadFile(
    name=n,
    mime_type=t,
    project=p,
  )
  try:
    yield tmp
  finally:
    kd.DeleteFile(uuid=tmp["uuid"])

def default_config():
  return {
    "domain": "http://localhost/api/",
    "username": "rodan",
    "password": "rodan",
    "proxy": ""
  }