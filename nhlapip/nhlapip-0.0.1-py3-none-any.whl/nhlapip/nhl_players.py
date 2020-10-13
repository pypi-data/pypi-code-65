from .nhl_url import NhlUrl
from .const import NHLAPI_BASEURL

class Player(NhlUrl):
    def __init__(self, id):
        super().__init__(endpoint = "people", suffixes = id)

    def get_data(self):
         self.get_data()
         self.data = self.data["people"][0]
         self.data
