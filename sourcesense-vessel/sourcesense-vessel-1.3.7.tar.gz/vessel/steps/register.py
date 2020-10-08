import requests
import uuid
import os
from typing import List, Callable
from vessel.pipeline import Step, Payload
from vessel.logging import logger

class RegisterStep(Step):
  """
  Register to Vessel api the cluster
  """

  def __init__(self, host):
    super().__init__()
    self.host = host

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    start_fn("Registering to api")
    
    rpc_payload = {
        "method": "agent.register",
        "params": {
          "t": payload.token,
          "iv": payload.vault_iv,
          "ct": payload.vault_ct,
          "pub": payload.rsa_pub
        },
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
    }
    response = requests.post(f"{self.host}", json=rpc_payload)
    if response.status_code >= 400 or response.json().get("error", False):
      raise Exception(response.text)

    payload.cluster = response.json()
    
    # save registration request
    start_fn("Saving registration")
    path = os.path.expanduser(f"~/.daas/{payload.token}")
    if not os.path.exists(path):
      os.mkdir( path )
    with open(f"{path}/registration.json", 'w') as f:
      f.write(payload.registration_json())

    end_fn(f"OK [ {path} ]")
    return payload
