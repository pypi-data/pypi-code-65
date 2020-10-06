from .resource import Resource
from .roomType import RoomType

class Room(Resource):
    def __init__(self, url, session, data={}):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "primaryKey", "RoomId")
        object.__setattr__(self, "url", url + "Room()")

    def type(self):
        if type(self.data['RoomType']) is RoomType:
            return self.data['RoomType']
        url = self.url[:-2] + f"Type()?$filter=RoomTypeId eq {self.data['RoomType']}"
        data = self.session.get(url)
        return RoomType(url, self.session, data.json()['value'][0])
