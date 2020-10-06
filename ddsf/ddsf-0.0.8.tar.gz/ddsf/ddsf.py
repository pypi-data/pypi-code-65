from requests import Session
from requests_ntlm import HttpNtlmAuth
from .user import User
from .person import Person
from .academicTitle import AcademicTitle
from .room import Room
from .roomType import RoomType
from .orgUnit import OrgUnit
from .orgUnitType import OrgUnitType

class Ddsf():
    """
    object that stores session

    Parameters
    ----------
    url
        dsf url
    username
        username to authentificate against dsf
    password
        password to authenticate
    """
    url = None
    session = None

    def __init__(self, url, username, password):
        self.url = url
        self.session = Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.auth = HttpNtlmAuth(username, password)

    def getSingle(self, entity, obj, filter=""):
        if filter:
            filter = "?$filter=" + filter
        response = self.session.get(self.url + entity + filter)
        print(obj)
        if not response.json()['value']:
            return None
        return obj(self.url, self.session, response.json()['value'][0])

    def getMultiple(self, entity, obj, filter=""):
        orgUnits = []

        response = self.session.get(self.url + entity + filter)
        if not response.json()['value']:
            return []

        # this loop runs minimum the first time(indicated by empty orgUnits) and repeats if the response contains a nextLink
        while not orgUnits or '@odata.nextLink' in response.json():
            if orgUnits:
                response = self.session.get(response.json()['@odata.nextLink'])

            for orgUnit in response.json()['value']:
                orgUnits.append(obj(self.url, self.session, orgUnit))

        return orgUnits


    def user(self, username):
        """
        find a user by username

        Args:
            username: zih-login

        Returns:
            User: a user object

        """
        user = User(self.url, self.session)
        print(user.session)
        user.get(username)
        return user

    def room(self, id, full=False):
        """
        get a specific room

        Args:
            id: RoomId to search for
            full: if True it will replace RoomType with the corresponding object

        Returns:
            Room: Room with the given id

        """
        room = Room(self.url, self.session)
        room.get(id, full)
        return room

    def rooms(self):
        """
        get all available rooms

        Returns:
            list[Room]: a list of Room

        """
        return self.getMultiple("Room()", Room, "?$filter=IsDeleted eq false")

    def orgUnits(self):
        """
        get all available orgUnits

        Returns:
            list[OrgUnit]: a list of OrgUnits

        """
        return self.getMultiple("OrgUnit()", OrgUnit, "?$filter=IsDeleted eq false")

    def orgUnitType(self, filter=""):
        """
        get all available orgUnitTypes

        Returns:
            list[OrgUnitType]: a list of OrgUnitType

        """
        return self.getSingle("OrgUnitType()", OrgUnitType, filter)

    def orgUnitTypes(self):
        """
        get all available orgUnitTypes

        Returns:
            list[OrgUnitType]: a list of OrgUnitType

        """
        return self.getMultiple("OrgUnitType()", OrgUnitType)

    def roomTypes(self):
        """
        get all available roomTypes

        Returns:
            list[RoomType]: a list of RoomType

        """
        return self.getMultiple("RoomType()", RoomType, "?$filter=IsDeleted eq false")

    def person(self, id):
        person = Person(self.url, self.session)
        person.get(id)
        return person

    def academicTitle(self, id=None):
        title = AcademicTitle(self.url, self.session)
        title.get(id)
        return title

    def get(self):
        return self.session.get(self.url).json()['value']
