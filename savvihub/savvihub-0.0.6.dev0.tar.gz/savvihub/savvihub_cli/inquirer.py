import re

from savvihub.savvihub_cli.constants import INQUIRER_NAME_IMAGE, INQUIRER_NAME_RESOURCE, INQUIRER_NAME_DATASET


def parse_id(choice):
    numbers = re.findall("[\d+]", choice)
    return numbers[0]

def parse_image_choice(image):
    first, second = image.image_url.split(':')
    return f'[{image.id}] savvihub/{second} | {image.name}'


def parse_resource_choice(resource):
    return f'[{resource.id}] {resource.name} | CPU: {resource.cpu_limit} | Memory: {resource.mem_limit}'


def parse_dataset_choice(dataset, dataset_type):
    return f'[{dataset.id}] {dataset.name} | {dataset_type}'


def get_choices(client, req_type, yml_loader):
    workspace = yml_loader.data.get('workspace')
    if req_type == INQUIRER_NAME_IMAGE:
        savvi_kernel_images = client.kernel_image_list(workspace)
        choices = [None for _ in savvi_kernel_images]
        for (i, image) in enumerate(savvi_kernel_images):
            choices[i] = parse_image_choice(image)
        return choices
    elif req_type == INQUIRER_NAME_RESOURCE:
        savvi_kernel_resources = client.kernel_resource_list(workspace)
        choices = [None for _ in savvi_kernel_resources]
        for (i, resource) in enumerate(savvi_kernel_resources):
            choices[i] = parse_resource_choice(resource)
        return choices
    elif req_type == INQUIRER_NAME_DATASET:
        savvi_public_dataset = client.public_dataset_list()
        savvi_private_dataset = client.dataset_list(workspace)
        choices = []
        for dataset in savvi_public_dataset:
            choices.append(parse_dataset_choice(dataset, 'public'))
        for dataset in savvi_private_dataset:
            choices.append(parse_dataset_choice(dataset, 'private'))
        return choices
    else:
        raise Exception('Wrong type!')

