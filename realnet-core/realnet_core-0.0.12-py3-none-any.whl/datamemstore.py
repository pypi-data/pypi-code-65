from .datastore import DataStore
from .data import Data

import uuid

class DataMemStore(DataStore):

    def __init__(self):
        self.data = {}

    def create_data(self, data, attributes=None):

        id = uuid.uuid4()
        new = Data(id, data, attributes)
        self.data[id] = new

        return new

    def put_data(self, data):

        self.data[data.id] = data

        return data

    def get_data(self, id):
        return self.data[id]

    def delete_data(self, id):
        return self.data.pop(id)

