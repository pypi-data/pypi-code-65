import os
import sys
import tempfile

import click
import docker
import stringcase
from bentoml.utils.lazy_loader import LazyLoader
from jinja2 import Environment, FileSystemLoader
from kubernetes import client, config

from bentoutils.kubeutil import from_yaml


@click.command()
@click.option('--module', help='fully qualified module name containing service to package')
@click.option('--clz', help='class name of service to package')
@click.option('--name', help='model name')
@click.option('--path', help='directory path of pretrained model')
def pack(module, clz, name, path):
    # Create a service instance
    svc = get_instance(module, clz)

    # Package the pretrained model artifact
    svc.pack(name, path)

    # Save the service to the model registry for serving
    saved_path = svc.save()

    # print('Saved model to ' + saved_path)


def get_instance(module_name, class_name):
    module = __import__(module_name)
    class_ = getattr(module, class_name)
    return class_()


yatai_proto = LazyLoader('yatai_proto', globals(), 'bentoml.yatai.proto')


@click.command()
@click.option('--bento', help='bento service name')
@click.option('--registry', help='registry name')
def deploy_to_knative(bento, registry):
    # Get saved path
    if ':' in bento:
        name, version = bento.split(':')
    else:
        name = bento
        version = 'latest'
    
    yatai_client = get_default_yatai_client()
    result = yatai_client.repository.get(name, version)
    if result.status.status_code != yatai_proto.status_pb2.Status.OK:
        error_code, error_message = status_pb_to_error_code_and_message(result.status)
        print(f'{error_code}:{error_message}')
        sys.exit(1)
    
    saved_path = result.bento.uri.uri

    # Build Docker image
    client = docker.from_env()
    tag = f'{registry}/{name}:{version}'
    client.images.build(path=saved_path, tag=tag)
    for line in client.push(tag, stream=True, decode=True):
        print(line)
    
    # Generate KNative manifest
    output_dir = tempfile.TemporaryDirectory(dir='/tmp')
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resources_dir = os.path.join(root_dir, 'templates/knative')
    env = Environment(loader=FileSystemLoader(resources_dir))
    template = env.get_template('service.yaml')
    svc_name = stringcase.spinalcase(name)
    yaml_file = os.path.join(output_dir, 'service.yaml')
    template.stream(name=svc_name, registry=registry).dump(yaml_file)

    # Deploy to KNative
    from_yaml(yaml_file)

    # Cleanup
    output_dir.cleanup()


def get_default_yatai_client():
    from bentoml.yatai.client import YataiClient

    return YataiClient()


# This function assumes the status is not status.OK
def status_pb_to_error_code_and_message(pb_status) -> (int, str):
    from bentoml.yatai.proto import status_pb2

    assert pb_status.status_code != status_pb2.Status.OK
    error_code = status_pb2.Status.Code.Name(pb_status.status_code)
    error_message = pb_status.error_message
    return error_code, error_message
