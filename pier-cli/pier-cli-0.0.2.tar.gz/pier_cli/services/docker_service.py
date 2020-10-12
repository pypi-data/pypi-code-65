import os
import io

import docker

from pier_cli.models.docker import Image


class DockerService:

    APP_LABEl = {'app': 'pier'}

    def __init__(self):
        self.client = docker.from_env()

    def list_images(self):
        return [
            Image.from_docker_image(di) for di in self.client.images.list()
            if di.labels.get('app', '') == 'pier' and di.attrs.get('RepoTags')
        ]

    def pull_image(self, tag):
        fileobj = io.BytesIO(bytes(f'FROM {tag}', 'utf-8'))
        self.client.images.build(fileobj=fileobj, rm=True, tag=tag, labels=self.APP_LABEl)

    def build_image(self, tag):
        path = os.path.abspath(os.getcwd())
        self.client.images.build(path=path, tag=tag, rm=True, labels=self.APP_LABEl)

    def remove_image(self, image):
        try:
            self.client.images.remove(image=image.id, force=True)
        except docker.errors.APIError as e:
            print('Unable to remove, make sure the image is not used anymore')
