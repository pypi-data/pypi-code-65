from .resource import Resource

class Person(Resource):
    def __init__(self, url, session):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", {})
        object.__setattr__(self, "primaryKey", "ActorId")
        object.__setattr__(self, "url", url + "Person()")
        object.__setattr__(self, "filter","?$filter=ActorId eq %d")

    def get(self, id):
        object.__setattr__(self, "id", id)
        data = self.session.get(self.url + self.filter % id)
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])
