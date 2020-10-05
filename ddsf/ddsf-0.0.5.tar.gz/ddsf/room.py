from .resource import Resource
from .roomType import RoomType

class Room(Resource):
    def __init__(self, url, session, data={}):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "url", url + "Room()")

    def get(self, id, full=False):
        data = self.session.get(self.url + f"?$filter=RoomId eq {id}")
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])
        #print(self.type())
        if full:
            newtype = self.type()
            self.data['RoomType'] = newtype

    def update(self):
        url = self.url[:-1] + f"{self.data['RoomId']})"
        data = self.session.patch(url, json=self.data)
        if data.status_code == 200:
            self.data = data.json()["value"][0]
        return data

    def type(self):
        if type(self.data['RoomType']) is RoomType:
            return self.data['RoomType']
        url = self.url[:-2] + f"Type()?$filter=RoomTypeId eq {self.data['RoomType']}"
        data = self.session.get(url)
        return RoomType(url, self.session, data.json()['value'][0])
