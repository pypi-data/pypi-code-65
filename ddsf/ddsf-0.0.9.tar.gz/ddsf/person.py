from .resource import Resource

class Person(Resource):
    def __init__(self, url, session):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", {})
        object.__setattr__(self, "primaryKey", "ActorId")
        object.__setattr__(self, "url", url + "Person()")
