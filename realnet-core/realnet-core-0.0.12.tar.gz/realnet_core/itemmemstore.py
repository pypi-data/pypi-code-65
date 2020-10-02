from .type import Type
from .item import Item
from .itemstore import ItemStore

import os
import uuid
import json


class ItemMemStore(ItemStore):

    def __init__(self, types={}, items={}):
        self.types = types
        self.items = items

    def create_type(self, name, items=None, data=None, attributes={}):
        references = []
        if items:
            references = [existing for existing in [self.items.get(item.id) for item in items] if existing]
        id = str(uuid.uuid4())
        new = Type(id, name, references, attributes)
        self.types[id] = new
        return new

    def retrieve_type(self, id):
        return self.types.get(id)

    def update_type(self, type):

        if type is None:
            return None

        self.types[type.id] = type
        return type

    def delete_type(self, id):
        return self.types.pop(id)

    def find_types(self, query, cursor):
        return None

    def create_item(self, type, name=None, attributes={}):

        if type is None:
            return None

        id = str(uuid.uuid4())
        new = Item(id, name if name else type.name, type, attributes)
        self.items[id] = new

        return new

    def retrieve_item(self, id):
        return self.items.get(id)

    def update_item(self, item):
        if item is None:
            return None

        self.items[item.id] = item

        return item

    def delete_item(self, id):
        return self.items.pop(id)

    def find_items(self, query, cursor):
        return None

    def save(self, path):
        out_types = {t[0]: {'id': t[1].id,
                            'name': t[1].name,
                            'items': [i.id for i in t[1].items],
                            'attributes': t[1].attributes} for t in self.types.items()}
        out_items = {i[0]: {'id': i[1].id,
                            'name': i[1].name,
                            'type': i[1].type.id,
                            'attributes': i[1].attributes} for i in self.items.items()}
        with open(path, 'w') as outfile:
            json.dump({'types': out_types, 'items': out_items}, outfile, indent=4, sort_keys=True)

    @classmethod
    def load(cls, path):
        if os.path.exists(path):
            with open(path, 'r') as json_file:
                data = json.load(json_file)
                in_types = {t[0]: Type(t[1]['id'],
                                       t[1]['name'],
                                       t[1]['items'],
                                       t[1]['attributes']) for t in data['types'].items()}
                in_items = {i[0]: Item(i[1]['id'],
                                       i[1]['name'],
                                       i[1]['type'],
                                       i[1]['attributes']) for i in data['items'].items()}
                for item in in_items:
                    in_items[item].type = in_types[item]

                for type in in_types:
                    in_types[type].items = [in_items[item] for item in in_types[type].items]

                return ItemMemStore(in_types, in_items)
        else:
            return ItemMemStore()

