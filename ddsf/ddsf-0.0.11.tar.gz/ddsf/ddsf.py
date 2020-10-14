from requests import Session
from requests_ntlm import HttpNtlmAuth
import pymssql
from .resource import *

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
    db = None

    def __init__(self, url, username, password):
        self.url = url
        self.session = Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.auth = HttpNtlmAuth(username, password)

    def connectdb(self, host, database, user, password):
        """
        initialize database connection for the use of non-dsf functions
        """
        self.db = pymssql.connect(host, user, password, database, autocommit=True)


    def getSingle(self, entity, obj, filter=""):
        if filter:
            filter = "?$filter=" + filter
        response = self.session.get(self.url + entity + filter)
        if not response.json()['value']:
            return None
        return obj(self.url, self.session, response.json()['value'][0], self.db)

    def getMultiple(self, entity, obj, filter=""):
        if filter:
            filter = "?$filter=" + filter
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
        return self.getSingle("UserAccount()",
                              User,
                              f"UserName eq '{username}'")

    def student(self, matric):
        """
        find a user by username

        Args:
            username: zih-login

        Returns:
            User: a user object

        """
        return self.getSingle("Student()",
                              Student,
                              f"MatriculationNumber eq '{matric}'")

    def room(self, id, full=False):
        """
        get a specific room

        Args:
            id: RoomId to search for
            full: if True it will replace RoomType with the corresponding object

        Returns:
            Room: Room with the given id

        """
        if not full:
            return self.getSingle("Room()",
                                  Room,
                                  f"RoomId eq {id}")
        room = self.getSingle("Room()",
                              Room,
                              f"RoomId eq {id}")
        room.RoomType = room.type()
        return room

    def rooms(self):
        """
        get all available rooms

        Returns:
            list[Room]: a list of Room

        """
        return self.getMultiple("Room()", Room, "IsDeleted eq false")

    def orgUnits(self, filter="IsDeleted eq false"):
        """
        get all available orgUnits

        Returns:
            list[OrgUnit]: a list of OrgUnits

        """
        return self.getMultiple("OrgUnit()", OrgUnit, filter)

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
        return self.getMultiple("RoomType()", RoomType, "IsDeleted eq false")

    def person(self, id):
        return self.getSingle("Person()", Person, f"ActorId eq {id}")

    def academicTitle(self, id=None):
        title = AcademicTitle(self.url, self.session)
        title.get(id)
        return title

    def get(self):
        return self.session.get(self.url).json()['value']
