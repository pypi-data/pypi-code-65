from .resource import Resource


class User(Resource):
    """
    represents User() entity

    Attributes:
        session(requests.Session): requests session
        data(dict): all userData is stored inside this dict
        url
        filter
    """
    def __init__(self, url, session, data={}):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "primaryKey", "UserAccountId")
        object.__setattr__(self, "url", url + "UserAccount()")
        object.__setattr__(self, "filter", "?$filter=UserName eq '%s'")
