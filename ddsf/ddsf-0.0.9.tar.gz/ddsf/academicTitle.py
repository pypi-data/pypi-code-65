from .resource import Resource

class AcademicTitle(Resource):

    def __init__(self, url, session):
        #self.session = session
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", {})
        object.__setattr__(self, "url", url + "AcademicTitle()")
        object.__setattr__(self, "filter", "?$filter=UserName eq '%d'")


    def get(self, id=None):
        object.__setattr__(self, "id", id)
        if id:
            data = self.session.get(self.url + self.filter % id)
            if data.status_code == 200:
                object.__setattr__(self, "data", data.json()["value"][0])
        else:
            data = self.session.get(self.url)
            if data.status_code == 200:
                object.__setattr__(self, "data", data.json()["value"])

    def update(self):
        data = self.session.patch(self.url[:-1] + f"{self.data['UserAccountId']})", data=self.data)
        if data.status_code == 200:
            self.data = data.json()["value"][0]
        return data
