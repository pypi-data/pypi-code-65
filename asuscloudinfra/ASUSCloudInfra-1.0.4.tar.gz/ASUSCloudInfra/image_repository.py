from .project import Project
class ImageRepository():
    def __init__(self, project):
        self._project = project
        self._actionPrefix = "/api/v1/image-svc/project/" + project.getProjectId() + "/"

    def getImageList(self, type="all"):
        action = self._actionPrefix + "image"
        body = self._project.get(action)
        imageList = None
        if type == "all":
            imageList = body['data']['public'] + body['data']['private']
        elif type == "public":
            imageList = body['data']['public']
        else:
            imageList = body['data']['private']
        return imageList

    def getImage(self, imageName):
        find = None
        imageList = self.getImageList()
        for image in imageList:
            if image["name"] == imageName:
                find = image
        return find

    def createImageTag(self, imageName, tagName):
        image = self.getImage(imageName)
        action = self._actionPrefix + "image/" + image['id'] + "/tag"

        body = { 
            'image': {'tag': tagName}
        }
        resp = self._project.post(action, body)
        #print(resp, flush=True)
        if "errorCode" in resp and resp['errorCode'] != None:
            print(resp['message'])
            return False
        return True
    
    def deleteImageTag(self, imageName, tagName):
        image = self.getImage(imageName)
        find = None
        for tag in image['tags']:
            if tag['tag'] == tagName:
                find = tag
        if find is not None:
            action = self._actionPrefix + "image/" + image['id'] + "/tag/" + str(find['id'])
            self._project.delete(action)
            return True
        return False