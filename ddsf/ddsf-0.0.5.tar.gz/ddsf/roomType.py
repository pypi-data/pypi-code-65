from .resource import Resource

class RoomType(Resource):
    def __init__(self, url, session, data={}):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "url", url + "RoomType()")

    def get(self):
        data = self.session.get(self.url)
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])

    def update(self):
        url = self.url[:-1] + f"{self.data['RoomId']})"
        data = self.session.patch(url, json=self.data)
        if data.status_code == 200:
            self.data = data.json()["value"][0]
        return data
