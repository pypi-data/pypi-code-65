from .type import Type
import json
import copy


class Item:
    def __init__(self, id, name, type, attributes={}):
        self.id = id
        self.name = name
        self.type = type
        self.attributes = dict(list(copy.deepcopy(self.type.attributes).items()) + list(attributes.items()))

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'type': self.type.to_dict(),
                'attributes': self.attributes if isinstance(self.attributes, dict) else {}}

    def to_json(self):
        return json.dumps(self.to_dict())

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # Ignoring .b attribute
            return self.id == other.id
        else:
            return NotImplemented

    def __repr__(self):
        return "Item(%s, %s, %s, %s)" % (self.id, self.name, self.type.__repr__(), self.attributes)

    @classmethod
    def from_dict(cls, data):
        return Item(data['id'],
                    data['name'],
                    Type.from_dict(data['type']),
                    data['attributes'])

    @classmethod
    def from_json(cls, data):
        t = json.loads(data)
        return Item(t['id'], t['name'], Type.from_dict(t['type']), t['attributes'])