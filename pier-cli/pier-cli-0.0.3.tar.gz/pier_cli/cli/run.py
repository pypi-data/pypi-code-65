import fire

from tabulate import tabulate

from pier_cli.services import DockerService, PodService
from pier_cli.utils import is_image, is_deployment


docker_service = DockerService()
pod_service = PodService()


class pier:

    def get(self, resource):
        if is_image(resource):
            data = [[image.name] for image in docker_service.list_images()]
            print(tabulate(data, headers=["Name"]))
        elif is_deployment(resource):
            data = [[deploy.name] for deploy in pod_service.list_deployments()]
            print(tabulate(data, headers=["Name"]))
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
            if image.ports:
                # TODO: Make ports configurable
                pod_service.create_service(resource_name, image.ports)
                ports = [f"http://localhost:{p}" for p in image.ports]
                print(f'Deployment reachable on: {ports}')
        else:
            print(f'Resource not supported')

    def delete(self, resource):
        if is_image(resource):
            image = self._single_select('image', docker_service.list_images())
            docker_service.remove_image(image)
        elif is_deployment(resource):
            deployment = self._single_select('deployment', pod_service.list_deployments())
            pod_service.delete_service(deployment)
            pod_service.delete_deployment(deployment)
        else:
            print(f'Resource not supported')

    def search(self, resource, term):
        if is_image(resource):
            data = [[si['name'], si['description'], si['star_count']] for si in docker_service.search(term)]
            print(tabulate(data, headers=["Name", "Description", "Stars"]))

    def _single_select(self, name, items):
        data = [[i, items[i].name] for i in range(0, len(items))]
        print(tabulate(data, headers=["Nr.", "Name"]))
        selected_item = input(f'\nSelect {name} nr.: ')
        return items[int(selected_item)]

def cli():
    fire.Fire(pier)
