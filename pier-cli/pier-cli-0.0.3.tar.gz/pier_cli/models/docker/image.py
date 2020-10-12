class Image:

    def __init__(self, id, tags, ports):
        self.id = id
        self.name = tags[0] if tags else ''
        self.tags = tags
        self.ports = ports

    @staticmethod
    def from_docker_image(docker_image):
        ports = []
        exposed_ports = docker_image.attrs.get('ContainerConfig').get('ExposedPorts')
        if exposed_ports:
            for port in exposed_ports.keys():
                ports.append(int(port.split('/')[0]))

        tags = docker_image.attrs.get('RepoTags')
        return Image(docker_image.id, tags, ports)
