class Image:

    def __init__(self, id, tags):
        self.id = id
        self.name = tags[0] if tags else ''
        self.tags = tags

    @staticmethod
    def from_docker_image(docker_image):
        # print(docker_image.attrs.get('ContainerConfig').get('ExposedPorts'))
        tags = docker_image.attrs.get('RepoTags')
        return Image(docker_image.id, tags) 
