"""
Type checkers for lesana fields.

Warning: this part of the code is still in flux and it may change
significantly in a future release.
"""
import datetime
import decimal
import logging

import dateutil.parser


class LesanaType:
    """
    Base class for lesana field types.
    """
    def __init__(self, field, types):
        self.field = field

    def load(self, data):
        raise NotImplementedError

    def empty(self):
        raise NotImplementedError


class LesanaString(LesanaType):
    """
    A string of unicode text
    """
    name = 'string'

    def load(self, data):
        if not data:
            return data
        return str(data)

    def empty(self):
        return ""


class LesanaText(LesanaString):
    """
    A longer block of unicode text
    """
    name = 'text'


class LesanaInt(LesanaType):
    """
    An integer number
    """
    name = "integer"

    def load(self, data):
        if not data:
            return data
        try:
            return int(data)
        except ValueError:
            raise LesanaValueError(
                "Invalid value for integer field: {}".format(data)
            )

    def empty(self):
        return 0


class LesanaFloat(LesanaType):
    """
    A floating point number
    """
    name = "float"

    def load(self, data):
        if not data:
            return data
        try:
            return float(data)
        except ValueError:
            raise LesanaValueError(
                "Invalid value for float field: {}".format(data)
            )

    def empty(self):
        return 0.0


class LesanaDecimal(LesanaType):
    """
    A floating point number
    """
    name = "decimal"

    def load(self, data):
        if not data:
            return data
        try:
            return decimal.Decimal(data)
        except decimal.InvalidOperation:
            raise LesanaValueError(
                "Invalid value for decimal field: {}".format(data)
            )

    def empty(self):
        return decimal.Decimal(0)


class LesanaTimestamp(LesanaType):
    """
    A unix timestamp
    """
    name = "timestamp"

    def load(self, data):
        if not data:
            return data
        if isinstance(data, datetime.datetime):
            return data
        try:
            return datetime.datetime.fromtimestamp(int(data))
        except (TypeError, ValueError):
            raise LesanaValueError(
                "Invalid value for timestamp field: {}".format(data)
            )

    def empty(self):
        return None


class LesanaDatetime(LesanaType):
    """
    A datetime
    """
    name = "datetime"

    def load(self, data):
        if not data:
            return data
        if isinstance(data, datetime.datetime):
            return data
        if isinstance(data, datetime.date):
            return datetime.datetime(data.year, data.month, data.day)
        try:
            return dateutil.parser.parse(data)
        except dateutil.parser.ParserError:
            raise LesanaValueError(
                "Invalid value for datetime field: {}".format(data)
            )

    def empty(self):
        return None


class LesanaDate(LesanaType):
    """
    A date
    """
    name = "date"

    def load(self, data):
        if not data:
            return data
        if isinstance(data, datetime.date):
            return data
        try:
            return dateutil.parser.parse(data)
        except dateutil.parser.ParserError:
            raise LesanaValueError(
                "Invalid value for date field: {}".format(data)
            )

    def empty(self):
        return None


class LesanaBoolean(LesanaType):
    """
    A boolean value
    """
    name = 'boolean'

    def load(self, data):
        if not data:
            return data
        if isinstance(data, bool):
            return data
        else:
            raise LesanaValueError(
                "Invalid value for boolean field: {}".format(data)
            )

    def empty(self):
        return None


class LesanaFile(LesanaString):
    """
    A path to a local file.

    Relative paths are assumed to be relative to the base lesana
    directory (i.e. where .lesana lives)
    """
    name = 'file'


class LesanaURL(LesanaString):
    """
    An URL
    """
    name = 'url'


class LesanaYAML(LesanaType):
    """
    Free YAML contents (no structure is enforced)
    """
    name = 'yaml'

    def load(self, data):
        return data

    def empty(self):
        return None


class LesanaList(LesanaType):
    """
    A list of other values
    """

    name = 'list'

    def __init__(self, field, types):
        super().__init__(field, types)
        try:
            self.sub_type = types[field['list']](field, types)
        except KeyError:
            logging.warning(
                "Unknown field type %s in field %s",
                field['type'],
                field['name'],
            )
            self.sub_type = types['yaml'](field, types)

    def load(self, data):
        if data is None:
            # empty for this type means an empty list
            return []
        try:
            return [self.sub_type.load(x) for x in data]
        except TypeError:
            raise LesanaValueError(
                "Invalid value for list field: {}".format(data)
            )

    def empty(self):
        return []


class LesanaValueError(ValueError):
    """
    Raised in case of validation errors.
    """
