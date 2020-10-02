import json

import realnet_core.item


class Type:

    def __init__(self, id, name, items=[], attributes=None):
        self.id = id
        self.name = name
        self.items = items
        self.attributes = attributes

        if id is None and items:
            self.id = items.__hash__()


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # Ignoring .b attribute
            return self.id == other.id
        else:
            return NotImplemented

    def __repr__(self):
        if self.name and (self.items or self.attributes):
            if self.items and self.attributes:
                return "Type(%s, %s, %s, %s)" % (self.id, self.name, [item.__repr__() for item in self.items], self.attributes)
            elif self.items:
                return "Type(%s, %s, %s)" % (self.id, self.name, [item.__repr__() for item in self.items])
            else:
                return "Type(%s, %s, %s)" % (self.id, self.name, self.attributes)
        elif self.name:
            return "Type(%s, %s)" % (self.id, self.name)
        else:
            return "Type(%s)" % (self.id)


    def create_item(self, id, name, attributes=None):
        return realnet_core.item.Item(id,
                                      name,
                                      self,
                                      attributes if attributes else {})

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'items': [item.to_dict() for item in self.items],
                'attributes': self.attributes if isinstance(self.attributes, dict) else {}}

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        return Type(data['id'],
                    data['name'],
                    [realnet_core.item.Item.from_dict(item) for item in data['items']],
                    data['attributes'])

    @classmethod
    def from_json(cls, data):
        t = json.loads(data)
        return Type(t['id'],
                    t['name'],
                    [realnet_core.item.Item.from_dict(item) for item in t['items']],
                    t['attributes'])

    # def myFun(arg1, arg2, arg3):
    #     print("arg1:", arg1)
    #     print("arg2:", arg2)
    #     print("arg3:", arg3)
    # args = ("Geeks", "for", "Geeks")
    # myFun(*args)
    # kwargs = {"arg1": "Geeks", "arg2": "for", "arg3": "Geeks"}
    # myFun(**kwargs)

    @classmethod
    def set(cls, *args):
        pass