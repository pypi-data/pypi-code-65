import fire

from pier_cli.services import DockerService, PodService
from pier_cli.utils import is_image, is_deployment


docker_service = DockerService()
pod_service = PodService()


class pier:

    def get(self, resource):
        if is_image(resource):
            images = docker_service.list_images()
            for image in images:
                print(image.name)
        elif is_deployment(resource):
            pods = pod_service.list_deployments()
            for pod in pods:
                print(pod.name)
        else:
            print(f'Resource not supported')

    def pull(self, resource, resource_name):
        if is_image(resource):
            images = docker_service.pull_image(resource_name)
        else:
            print(f'Resource not supported')

    def create(self, resource, resource_name):
        if is_image(resource):
            docker_service.build_image(resource_name)
        elif is_deployment(resource):
            image = self._single_select('image', docker_service.list_images())
            pod_service.create_deployment(resource_name, image)
        else:
            print(f'Resource not supported')

    def delete(self, resource):
        if is_image(resource):
            image = self._single_select('image', docker_service.list_images())
            docker_service.remove_image(image)
        elif is_deployment(resource):
            deployment = self._single_select('deployment', pod_service.list_deployments())
            pod_service.delete_deployment(deployment)
        else:
            print(f'Resource not supported')

    def _single_select(self, name, items):
        select_item_txt = f'Select {name}:'
        for i in range(0, len(items)):
            item = items[i]
            select_item_txt = f'{select_item_txt} \n [{i}] - {item.name}'
        select_item_txt += '\n'
        selected_item = input(select_item_txt)
        return items[int(selected_item)]

def cli():
    fire.Fire(pier)
