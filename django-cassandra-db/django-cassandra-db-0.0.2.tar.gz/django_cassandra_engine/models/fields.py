from cassandra.cqlengine import columns
from cassandra.cqlengine.columns import *


class Blob(columns.Blob):

    choices = None

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


Bytes = Blob


class Inet(columns.Inet):

    choices = None

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Text(columns.Text):

    choices = None

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Ascii(columns.Ascii):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Integer(columns.Integer):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class TinyInt(columns.TinyInt):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class SmallInt(columns.SmallInt):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class BigInt(columns.BigInt):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class VarInt(columns.VarInt):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Counter(columns.Counter):

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class DateTime(columns.DateTime):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Date(columns.Date):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Time(columns.Time):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Duration(columns.Duration):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class UUID(columns.UUID):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class TimeUUID(columns.TimeUUID):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Boolean(columns.Boolean):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class BaseFloat(columns.BaseFloat):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Float(columns.Float):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Double(columns.Double):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Decimal(columns.Decimal):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Tuple(columns.Tuple):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Set(columns.Set):

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class List(columns.List):

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)


class Map(columns.Map):

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop('verbose_name', None)

        super().__init__(*args, **kwargs)
