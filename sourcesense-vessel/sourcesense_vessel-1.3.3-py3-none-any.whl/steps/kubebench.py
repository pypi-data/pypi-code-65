from typing import List, Callable
from vessel.pipeline import Step, Payload
from vessel.steps import VaultBaseStep
from vessel.logging import logger
import subprocess
import hvac
import base64
import os.path

class KubebenchStep(VaultBaseStep):
  """
  Unseal Vault Step
  """
  def get_rw_token(self, data):
    return base64.b64decode(data['private']['rw-token']).decode("utf-8")

  def __init__(self, vault_host, vault_info, yaml_dir):
    super().__init__(vault_host)
    self.vault_info = vault_info
    self.yaml_dir = yaml_dir
    #self.unlocked = unlocked

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    start_fn('Taking Vault root token')
    
    keys = self.get_vault_keys(payload, start_fn, prompt_fn)
    root_token = keys['root_token']
    self.vault.token = keys["root_token"]
    cluster_token = payload.token

    start_fn(root_token)
    start_fn(f"Cluster token is {cluster_token}. Taking k8s auth token from Vault")

    unlock_pub_secrets = self.vault.secrets.kv.v2.read_secret_version(
      path=cluster_token + "-daas-rw-ops",
      mount_point="daas_public"
    )

    pub_data = unlock_pub_secrets['data']['data']

    auth_token = pub_data['token']
    sa_name = pub_data['sa-name']
    distribution = pub_data['distribution']
    namespace = pub_data['namespace']

    start_fn(f"Cluster distribution of {cluster_token} is {distribution}")
    start_fn(f"Using the service account {sa_name} for installing kube-bench into the namespace {namespace}")

    if distribution == 'kubernetes':
      job_path = os.path.join(self.yaml_dir, 'k8s.yaml')
      bashCommand = f"kubectl -n {namespace} apply -f {job_path} --token={auth_token}"

    elif distribution == 'openshift':
      job_path = os.path.join(self.yaml_dir, 'ocp-3.11.yaml')
      bashCommand = f"oc -n {namespace} apply -f {job_path} --token={auth_token}"
  
    start_fn(f"Kube Bench yaml job path is {job_path}")
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
      raise Exception(error)
    for out in output.decode('utf-8').split("\n"):
      end_fn(out)

    end_fn(f"Job {job_path} applied!")
