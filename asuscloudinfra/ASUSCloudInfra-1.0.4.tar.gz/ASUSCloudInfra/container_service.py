from .project import Project
from .image_repository import ImageRepository
class ContainerService():
    def __init__(self, project):
        self._project = project
        self._actionPrefix = "/api/v1/containers/projects/" + project.getProjectId() + "/"
        self._imageRepository = ImageRepository(project)

    def getContainerList(self, imageName=None):
        action = self._actionPrefix
        body = self._project.get(action)
        containerList = []
        if imageName is None:
            containerList = body
        else:
            image = self._imageRepository.getImage(imageName)
            #print(image['path'], flush=True)
            for container in body:
                #print("imageName:" + container['imageName'])
                lastIndex = container['imageName'].rfind(':')
                #print("index:" + str(lastIndex))
                imageName = container['imageName'][:lastIndex]
                #print("imageName:" + imageName)
                if imageName == image['path']:
                    print('find')
                    containerList.append(container)
        return containerList
    
    def updateContainerImage(self, containers, imageName, tag):
        image = self._imageRepository.getImage(imageName)
        imageName = image['path'] + ":" + tag
        body = {
            "imageName": imageName
        }
        print(body)
        for container in containers:
            print(container["id"])
            print(container["name"])
            print(container["imageName"])
            action = self._actionPrefix + str(container["id"])
            self._project.patch(action, body)
