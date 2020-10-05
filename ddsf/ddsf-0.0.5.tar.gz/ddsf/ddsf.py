from requests import Session
from requests_ntlm import HttpNtlmAuth
from .user import User
from .person import Person
from .academicTitle import AcademicTitle
from .room import Room
from .roomType import RoomType
from .orgUnit import OrgUnit

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
        response = self.session.get(self.url + "Room()?$filter=IsDeleted eq false")
        roomList = []
        for room in response.json()['value']:
            roomList.append(Room(self.url, self.session, room))
        return roomList

    def orgUnits(self):
        """
        get all available orgUnits

        Returns:
            list[OrgUnit]: a list of OrgUnits

        """
        orgUnits = []

        response = self.session.get(self.url + "OrgUnit()")
        if not response.json()['value']:
            return []

        # this loop runs minimum the first time(indicated by empty orgUnits) and repeats if the response contains a nextLink
        while not orgUnits or '@odata.nextLink' in response.json():
            if orgUnits:
                response = self.session.get(response.json()['@odata.nextLink'])

            for orgUnit in response.json()['value']:
                orgUnits.append(OrgUnit(self.url, self.session, orgUnit))

        return orgUnits

    def roomTypes(self):
        response = self.session.get(self.url + "RoomType()?$filter=IsDeleted eq false")
        roomList = []
        for room in response.json()['value']:
            roomList.append(RoomType(self.url, self.session, room))
        return roomList

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
