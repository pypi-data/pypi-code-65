from copy import deepcopy
from basic_http.exceptions.structures import KeyNotFound


class MultiKeyDictionary(object):
    def __init__(self, data=None):
        self.__data = list()

        if data:
            self.update(data)

    def __len__(self):
        return len(self.__data)

    def __setitem__(self, key, value):
        new_data = list()
        new_item_set = False

        value = self.__format_value_as_iterable(value)

        for i in range(len(self)):
            if self.__data[i][0] != key:
                new_data.append(deepcopy(self.__data[i]))
            elif not new_item_set:
                new_data.extend([(key, v) for v in value])
                new_item_set = True
        else:
            if not new_item_set:
                new_data.extend([(key, v) for v in value])

        self.__data = deepcopy(new_data)

    def __getitem__(self, item):
        if item not in self:
            raise KeyNotFound(f'Key does not exist: {item}')

        for entry in self.__data:
            if entry[0] == item:
                yield entry[1]

    def __iter__(self):
        for entry in self.__data:
            yield entry[0]

    def __str__(self):
        keys = [f'\'{k}\'' if isinstance(k, str) else k for k, v in self.__data]
        values = [f'\'{v}\'' if isinstance(v, str) else v for k, v in self.__data]

        return '{' + ', '.join([f'{k}: {v}' for k, v in map(lambda x, y: (x, y), keys, values)]) + '}'

    @staticmethod
    def __format_value_as_iterable(value):
        if isinstance(value, str):
            return [value]

        try:
            value = list(value)
        except TypeError:
            value = [value]

        return value

    def add(self, key, value):
        value = self.__format_value_as_iterable(value)
        self.__data.extend((key, v) for v in value)

    def update(self, data):
        for key in data:
            if key not in self:
                self.add(key, data[key])
            else:
                self[key] = data[key]

    def items(self):
        return [(key, value) for key, value in self.__data]
