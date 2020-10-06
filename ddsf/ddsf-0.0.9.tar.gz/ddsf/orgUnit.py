from .resource import Resource

class OrgUnit(Resource):
    def __init__(self, url, session, data={}):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "primaryKey", "OrgUnitId")
        object.__setattr__(self, "url", url + "OrgUnit()")

    def get(self, id):
        data = self.session.get(self.url + f"?$filter=OrgUnitId eq {id}")
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])
