import os
import sys
import datetime
import yaml
import json
import logging
from kubernetes import client, config


def get_my_ns():
    ns_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    my_ns = None
    with open(ns_path) as f:
        my_ns = f.read()
    assert my_ns is not None
    return my_ns


def get_hostname():
    return os.getenv("HOSTNAME")


def delete_portmap_by_prefix(relative_prefix):
    logging.debug(f"delete_portmap_by_prefix: {relative_prefix}")
    rp = relative_prefix
    name = rp.replace("/", "-")
    vs_name = name
    svc_name = name
    try:
        _delete_portmap_service(svc_name)
    except:
        logging.warning("Unexpected error:", sys.exc_info()[0])
    try:
        _delete_portmap_virtual_service(vs_name)
    except:
        logging.warning("Unexpected error:", sys.exc_info()[0])
    return True


def _delete_portmap_service(svc_name):
    logging.debug(f"_delete_portmap_service: {svc_name}")
    my_ns = get_my_ns()
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    try:
        v1.delete_namespaced_service(name=svc_name, namespace=my_ns)
        logging.debug(f"delete_portmap success: {svc_name}")
        return True, svc_name
    except:
        pass
    return False, svc_name


def create_portmap(relative_prefix, port):
    pod_name = get_hostname()
    ns = get_my_ns()
    rp = relative_prefix
    prefix = f"/app/{ns}/{rp}"
    name = rp.replace("/", "-")
    vs_name = name
    svc_name = name
    _create_portmap_service(svc_name, pod_name, port)
    _create_portmap_virtual_service(vs_name, prefix, svc_name, port)
    return True, prefix


def _create_portmap_service(svc_name, pod_name, port):
    logging.debug(f"_create_portmap_service: {svc_name}, {pod_name}, {port}")
    # pod_name = get_hostname()
    my_ns = get_my_ns()

    config.load_incluster_config()
    v1 = client.CoreV1Api()
    spec = client.V1ServiceSpec()
    # spec.type = "NodePort"
    spec.selector = {"statefulset.kubernetes.io/pod-name": pod_name}
    spec.ports = [client.V1ServicePort(
        protocol="TCP", port=port, target_port=port)]

    s = client.V1Service()
    s.api_version = "v1"
    s.kind = "Service"
    s.metadata = client.V1ObjectMeta(name=svc_name)
    s.spec = spec

    v1.create_namespaced_service(namespace=my_ns, body=s)
    # field_selector = f"metadata.name={svc_name}"
    # ret = v1.list_namespaced_service(
    #     namespace=my_ns, field_selector=field_selector)
    # node_port = ret.items[0].spec.ports[0].node_port
    # return svc_name, node_port
    return True


def _delete_portmap_virtual_service(name):
    logging.debug(f"_delete_portmap_virtual_service: {name}")
    config.load_incluster_config()
    api = client.CustomObjectsApi()
    ns = get_my_ns()
    api.delete_namespaced_custom_object(
        group="networking.istio.io",
        version="v1alpha3",
        namespace=ns,
        plural="virtualservices",
        name=name)


def _create_portmap_virtual_service(vs_name, prefix, svc_name, port):
    logging.debug(f"_create_portmap_virtual_service: {vs_name}, {prefix}, {port}")
    config.load_incluster_config()
    api = client.CustomObjectsApi()
    ns = get_my_ns()
    body = f"""
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: {vs_name}
  namespace: {ns}
spec:
  gateways:
  - kubeflow/kubeflow-gateway
  hosts:
  - '*'
  http:
  - match:
    - uri:
        prefix: {prefix}
    rewrite:
      uri: /
    route:
    - destination:
        host: {svc_name}
        port:
          number: {port}
    """
    body = yaml.safe_load(body)
    api.create_namespaced_custom_object(
        group="networking.istio.io",
        version="v1alpha3",
        namespace=ns,
        plural="virtualservices",
        body=body
    )


def list_portmap_raw():
    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    my_ns = get_my_ns()
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_service(namespace=my_ns)
    return ret


def list_portmap():
    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    my_ns = get_my_ns()
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_service(namespace=my_ns)
    s = json.dumps(ret.to_dict(), default=default)
    return json.loads(s)


def list_virtual_service():
    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    my_ns = get_my_ns()
    config.load_incluster_config()
    api = client.CustomObjectsApi()
    ret = api.list_namespaced_custom_object(
        group="networking.istio.io", 
        version="v1alpha3", 
        namespace=my_ns,
        plural="virtualservices")
    s = json.dumps(ret, default=default)
    return json.loads(s)


def list_existing_virtual_service():
    d = list_virtual_service()
    items = d['items']
    exists = [
        item['spec']['http'][0]['match'][0]['uri']['prefix'] 
        for item in items]
    return exists


def is_exist_virtual_service(full_path):
    exists = list_existing_virtual_service()
    return full_path in exists


if __name__ == "__main__":
    # This is ugly dirty area
    relative_prefix = "shhong-path"
    port = 7777
    delete_portmap_by_prefix(relative_prefix)
    create_portmap(relative_prefix, port)