from typing import List, Callable
import json
import click


from vessel.logging import logger

class Payload(object):
  def __init__(self, token:str = None):
    if token and token.startswith("~"): # ~/.daas/TOKEN
      token = token.split("/")[2]
    if token and token.startswith("/"): # /home/rke/.daas/.daas/TOKEN
      token = token.split("/")[4]
    self.token:str = token
    self.serviceaccount = []
    self.vault_ct = None
    self.vault_iv = None
    self.vault_user = None
    self.vault_pwd  = None
    self.rsa_pub:str = None
    self.rsa:str = None
    self.cluster = None
    self.distribution = "kubernetes"
    self.agent_yaml = None
    self.sentinel_yaml = None

  def __str__(self):
    return json.dumps(self.__dict__)

  def registration_json(self):
    return json.dumps({
      "token": self.token,
      "rsa_pub": self.rsa_pub,
      "rsa":  self.rsa,
      "distribution": self.distribution,
      "cluster": self.cluster
    })


class Step(object):
  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable) -> Payload:
    raise Exception("Must implement")

class Pipeline(object):
  def __init__(self, start_fn=print, end_fn=print, prompt_fn=input):
    self.steps:List[Step] = []
    self.start_fn = start_fn
    self.end_fn = end_fn
    self.prompt_fn = prompt_fn

  def add(self, step:Step):
    self.steps.append(step)

  def run(self, start_payload:Payload):
    result:Payload = start_payload
    for step in self.steps:
      result = step.run(result, self.start_fn, self.end_fn, self.prompt_fn)
    
    return result
      
      
