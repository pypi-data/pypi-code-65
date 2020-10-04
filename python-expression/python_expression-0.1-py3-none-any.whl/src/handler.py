from datetime import datetime


class Handler():

    def __init__(self, data = {}):
        self._data = data


class EqualsHandler(Handler):

    def handle(self, condition):

        key = self._data.get(condition.key)
        key = key if key else condition.key

        return str(key) == str(condition.value)


class InHandler(Handler):

    def handle(self, condition):
        key = self._data.get(condition.key)
        key = key if key else condition.key

        values = condition.value.split(',')
        key = str(key)

        return key in values


class DateBetweenHandler(Handler):

    def handle(self, condition):
        key = self._data.get(condition.key)
        values = condition.value.split(',')

        date1 = datetime.strptime(values[0], '%Y-%M-%d')
        date2 = datetime.strptime(values[1], '%Y-%M-%d')

        return date1 <= key <= date2
