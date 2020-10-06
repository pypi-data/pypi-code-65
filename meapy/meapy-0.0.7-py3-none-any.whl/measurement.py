class Measurement(object):
    def __init__(self, document: dict):
        self.document = document
        pass

    def getType(self) -> str:
        return self.document.get('type')

    def getId(self) -> str:
        return self.document.get('id')

    def getDocument(self) -> dict:
        return self.document.get('fields')
