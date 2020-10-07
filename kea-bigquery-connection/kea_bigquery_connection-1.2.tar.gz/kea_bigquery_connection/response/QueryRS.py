from cerberus.responses.BodyRS import BodyRS

class QueryRS(BodyRS):

    def __init__(self, success, error=None):
        BodyRS.__init__(self, success, error)

    def getResponseData(self):
        return self.__responseData

    def setResponseData(self,responseData):
        self.__responseData = responseData
        self.update(responseData=responseData)
    