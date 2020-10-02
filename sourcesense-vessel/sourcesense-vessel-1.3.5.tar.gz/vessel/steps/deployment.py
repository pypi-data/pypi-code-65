import requests
import uuid
import os
import textwrap
import json
import subprocess
import urllib
import jinja2
import pkgutil
from typing import List, Callable, Tuple
from vessel.pipeline import Step, Payload
from vessel.logging import logger
from vessel.version import LATEST_AGENT, LATEST_SENTINEL, LATEST_EVENT_ENGINE
from vessel.utilities import sanitizeClusterName


class DeployStep(Step):
  """
  Deploy generated yaml
  """

  def __init__(self, resource):
    super().__init__()
    self.resource = resource

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    start_fn("Deploying sentinel")
    if payload.token:
      yaml = os.path.expanduser(f"~/.daas/{payload.token}/{self.resource}.yaml")
    else:
      yaml = os.path.expanduser(f"~/.daas/{self.resource}.yaml")
    bashCommand = f"kubectl -n daas apply -f {yaml}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
      raise Exception(error)
    for out in output.decode('utf-8').split("\n"):
      end_fn(out)
    return payload

class GenerateYamlStep(Step):
  """
  Generate kube deployments for agent & sentinel
  """

  def __init__(self, resource, tag, more_vars=dict()):
    super().__init__()
    self.resource = resource
    self.tag = tag
    self.more_vars:dict = more_vars

  def _get_keys(self, payload:Payload) -> Tuple[str]:
    if payload.rsa:
      name = sanitizeClusterName(payload.cluster['result']['name'])
      return (name, payload.rsa, payload.vault_user, payload.vault_pwd, payload.distribution)
    else:
      with open(os.path.expanduser(f"~/.daas/{payload.token}/registration.json"), 'r') as f:
        registration = json.load(f)
      with open(os.path.expanduser(f"~/.daas/vault.json"), 'r') as f:
        vault = json.load(f)
      
      name = sanitizeClusterName(registration['cluster']['result']['name'])
      return (name, registration['rsa'], vault['public']['user'], vault['public']['pwd'], registration['distribution'])

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    
    
    if payload.token is not None:
      start_fn("Loading keys")
      path = os.path.expanduser(f"~/.daas/{payload.token}")
      (name, rsa, vault_user, vault_pwd, distribution) = self._get_keys(payload)

      tpl_vars = {
        "name": name, 
        "token": payload.token, 
        "rsa": rsa.replace("\n", "\\n"), 
        "vault_password": vault_pwd, 
        "distribution": distribution, 
        "tag": self.tag
      }
    else:
      path = os.path.expanduser(f"~/.daas")
      tpl_vars = {}

    tpl_vars.update(self.more_vars)
    

    
    start_fn(f"generating {self.resource} yaml")
    data = pkgutil.get_data(__name__, f"../resources/{self.resource}.yaml.jinja2")
    
    template = jinja2.Template(data.decode("utf-8"))
    # template = templateEnv.get_template(f"{self.resource}.yaml.jinja2")
    yaml = template.render(tpl_vars)
        
    with open(f"{path}/{self.resource}.yaml", 'w') as f:
      f.write(yaml)

    end_fn("OK")

    return payload
