import copy
import json
import builtins

"""Struct class to handle complex JSON-style data structures"""


class Struct:
    def __init__(self, data=None):
        if data is None:
            self.data = {}
        elif type(data) != dict and type(data) != list:
            self.data = deserialize(data)
        else:
            self.data = data

    def dumps(self, indent=None):
        """Serialize self.data to json formatted str"""
        return json.dumps(self.data, indent=indent)

    @staticmethod
    def loads(string):
        """Returns Struct object from JSON str"""
        return Struct(json.loads(string))

    def dump(self, file, indent=None):
        """Serialize self.data to JSON formatted str, and writes it into file"""
        json.dump(self.data, file, indent=indent)

    @staticmethod
    def load(file):
        """Reads Struct data from file"""
        return Struct(json.load(file))

    def __repr__(self):
        """self.__repr__() --> str(self)"""
        return self.dumps(indent=4)

    def __setitem__(self, path, value):
        """self.__setitem__((path, to, value), value) --> self[path, to, value]=value"""
        if type(path) == tuple:
            path = list(path)
        elif type(path) != list:
            path = [path]
        modifyStruct(self.data, list(path) + [value])

    def __delitem__(self, path):
        if type(path) == tuple:
            path = list(path)
        elif type(path) != list:
            path = [path]
        delItem(self.data, path)

    def __contains__(self, key):
        """Returns (key in self)"""
        return isKeyIn(self.data, key)

    def __getitem__(self, path):
        """self.__getitem__(path) --> self[path]"""
        if type(path) == tuple:
            path = list(path)
        elif type(path) != list:
            path = [path]
        return getItem(self.data, list(path))

    def __iter__(self):
        """Returns the iterable equivalent of self"""
        if type(self.data) == dict:
            return [(k, self.data[k]) for k in self.data].__iter__()
        elif type(self.data) == list:
            return self.data.__iter__()
        else:
            return [self.data].__iter__()

    def __len__(self):
        n = 0
        for _ in self.data:
            n += 1
        return n

    def sorted(self, path=None, function=lambda x: x):
        """Returns the sorted Struct version of self. path: the path to the value which is looked at for the sort. If
        left as None and self.data is a dict object, the sort will look at the keys.
        function: the function applied on said value
        """
        if type(self.data) == list:
            if path is None:
                return Struct(sorted(self.data, key=function))
            else:
                return Struct(sorted(self.data, key=lambda x: function(Struct(x)[path])))
        else:
            result = Struct({})
            if path is None:
                for e in sorted(self, key=lambda x: function(x[0])):
                    result[e[0]] = e[1]
            else:
                for e in sorted(self, key=lambda x: function(Struct(x[1])[path])):
                    result[e[0]] = e[1]
            return result

    def sort(self, path=None, function=lambda x: x):
        """Sorts self.
        path: the path to the value which is looked at for the sort
        function: the function applied on said value (only works if path!=None)"""
        self.data = self.sorted(path, function).data

    def isValueIn(self, value):
        """Returns true if value is present in self.data"""
        return isValueIn(self.data, value)

    def pathToValue(self, value):
        """Returns the path to value as a list object (if it exists).
        Returns None if the value couldn't be found"""
        return pathToValue(self.data, value)

    def getAll(self, key):
        """Returns all values corresponding to key in a list object"""
        return getAll(self.data, key)

    def replace(self, old, new):
        """Returns a copy of self with the first occurrence of old replaced by new"""
        result = copy.deepcopy(self)
        if (path := result.pathToValue(old)) is not None:
            del path[-1]
            result[path] = new
        return result

    def replaceAll(self, old, new):
        """Returns a copy of self with all occurrences of old replaced by new"""
        result = copy.deepcopy(self)
        while (path := result.pathToValue(old)) is not None:
            del path[-1]
            result[path] = new
        return result


def getItem(data: 'JSON style object', path):
    """Returns value at path in data object"""
    if not path:
        return data
    return getItem(data[path[0]], path[1:])

def delItem(data: "JSON style object", path):
    # print(len(path)
    if not path:
        raise KeyError("Invalid path")
    elif len(path) == 1:
        del data[path[0]]
    else:
        delItem(data[path[0]], path[1:])

def deserialize(obj):
    data = {}
    defaultTypes = [
        int,
        str,
        float,
        bool,
        list,
        dict,
        complex,
        tuple
    ]
    excludedTypes = [
        "function",
        "builtins.staticmethod",
        "classmethod",
        "builtin_function_or_method",
        "method-wrapper",
        "NoneType"
    ]
    attrs = dir(obj)
    attrs.remove('__class__')
    attrs.remove('__doc__')
    for attr in attrs:
        v = obj.__getattribute__(attr)
        if type(v) in defaultTypes:
            data[attr] = v
        elif type(v).__name__ not in excludedTypes:
            data[attr] = str(v)
    return data


def modifyStruct(data: 'JSON style object', path):
    if len(path) == 2:
        data[path[0]] = path[1]
        return data
    if type(data) == dict:
        data.setdefault(path[0], {})
    data[path[0]] = modifyStruct(data[path[0]], path[1:])
    return data


def isValueIn(data: 'JSON style object', value):
    if data == value:
        return True

    elif type(data) == list:
        for x in data:
            if isValueIn(x, value):
                return True
        return False
    elif type(data) == dict:
        for k in data:
            if isValueIn(data[k], value):
                return True
    return False


def pathToValue(data: 'JSON style object', value):
    if data == value:
        return [value]

    if type(data) == dict:
        sequence = data.keys()
    else:
        sequence = range(len(data))

    for k in sequence:
        if isValueIn((sub := data[k]), value):
            return [k] + pathToValue(sub, value)


def isKeyIn(data: 'JSON style object', key):
    sequence = []
    if type(data) == list:
        sequence = range(len(data))
    elif type(data) == dict:
        sequence = data.keys()
    for k in sequence:
        if k == key:
            return True
        elif isKeyIn(data[k], key):
            return True
    return False


def getAll(data: 'JSON style object', key):
    sequence = []
    if type(data) == list:
        sequence = range(len(data))
    elif type(data) == dict:
        sequence = data.keys()
    values = []
    for k in sequence:
        if k == key:
            values.append(data[k])
        else:
            values += getAll(data[k], key)
    return values


if __name__ == "__main__":
    help(Struct)
