import os
import json
import kubernetes
from urllib.parse import urljoin
from vessel.pipeline import Step, Payload
from typing import List, Callable, Tuple
from vessel.logging import logger
from vessel.utilities import sanitizeClusterName

class UpdateStep(Step):
  """
  Deploy Agent
  """
  def __init__(self, agent_tag, sentinel_tag):
    super().__init__()
    self.agent_tag = agent_tag
    self.sentinel_tag = sentinel_tag


  def patch_image(self, component, deployment, namespace, image, kube_apps):
    try:
        body = {
          "spec": {
            "template": {
              "spec": {
                "containers": [
                  {
                    "name": deployment,
                    "image": image
                    }
                ]
              }
            }
          }
        }
        api_response = kube_apps.patch_namespaced_deployment(deployment, namespace, body)
    except ApiException as e:
        print("Exception when calling AppsV1Api->patch_namespaced_deployment: %s\n" % e)


  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    
    with open(os.path.expanduser('~/.vessel/devops.json')) as f:
      devops = json.load(f)

    with open(os.path.expanduser(f"~/.daas/{payload.token}/registration.json"), 'r') as f:
      registration = json.load(f)

    namespace = devops['vessel_namespace']
    img_base = devops['images_base_url']
    k8s_token = devops['devops_sa_token']
    cluster_name = sanitizeClusterName(registration['cluster']['result']['name'])
    
    # Init kube client
    start_fn('Creating kubernetes client configuration...')
    configuration = kubernetes.client.Configuration()
    configuration.host = devops['kubernetes_url']
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + k8s_token}
    api_client = kubernetes.client.ApiClient(configuration)
    apps = kubernetes.client.AppsV1Api(api_client)

    agent_deployment = cluster_name + '-agent'
    sentinel_deployment = cluster_name + '-sentinel'
    running_agent = apps.read_namespaced_deployment(agent_deployment, namespace).spec.template.spec.containers[0].image
    start_fn('At moment, you are running this tag image for Vessel Agent => ' + running_agent.split(":")[-1] )
    running_sentinel = apps.read_namespaced_deployment(sentinel_deployment, namespace).spec.template.spec.containers[0].image
    start_fn('At moment, you are running this tag image for Vessel Sentinel => ' + running_sentinel.split(":")[-1] )

    if running_agent.split(":")[-1] != self.agent_tag:
      end_fn('Updating Agent to tag ' + self.agent_tag)
      image = urljoin(img_base, 'workstation-agent') + ':' + self.agent_tag
      self.patch_image('Agent', agent_deployment, namespace, image, apps)
    else:
      end_fn('Agent is already updated')

    if running_sentinel.split(":")[-1] != self.sentinel_tag: 
      end_fn('Updating Sentinel to tag ' + self.sentinel_tag)
      image = urljoin(img_base, 'workstation-sentinel') + ':' + self.sentinel_tag
      self.patch_image('Sentinel', sentinel_deployment, namespace, image, apps)
    else:
      end_fn('Sentinel is already updated')