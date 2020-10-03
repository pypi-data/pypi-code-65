from django.db.models.fields import NOT_PROVIDED
from django.db import models
from django.core.exceptions import ValidationError
import datetime
import uuid
from rs4.attrdict import AttrDict
from sqlphile.sql import SQL, D
from sqlphile.q import _Q
from sqlphile.model import AbstractModel
from skitai import was
from rs4.annotations import classproperty, override

TZ_LOCAL = datetime.datetime.now (datetime.timezone.utc).astimezone().tzinfo
TZ_UTC = datetime.timezone.utc

TYPE_MAP = [
    (models.CharField, str, 'string'),
    ((models.IntegerField, models.AutoField), int, 'integer'),
    (models.FloatField, float, 'float'),
    (models.BooleanField, bool, 'boolean'),
    (models.DateTimeField, datetime.datetime, 'datetime'),
    (models.DateField, datetime.date, 'date'),
    (models.TimeField, datetime.time, 'time'),
    (models.UUIDField, uuid.UUID, 'uuid'),
]

def utcnow ():
    return datetime.datetime.now ().astimezone (TZ_UTC)

class TableInfo:
    def __init__ (self, name, columns):
        self.name = name
        self.columns = columns
        self.pk = None
        self.fks = {}

        for field in self.columns.values ():
            if field.pk:
                self.pk = field
            if field.related_model:
                self.fks [field.name] = (field.column, field.related_model)


class Model (AbstractModel, models.Model):
    _table_info_cache = None
    _alias = '@rdb'

    class Meta:
        abstract = True

    @classmethod
    @override
    def get_table_name (cls):
        return cls._meta.db_table

    @classmethod
    @override
    def get_pk (cls):
        return cls.get_table_info ().pk.column

    @classmethod
    @override
    def get_fks (cls):
        return cls.get_table_info ().fks

    @classmethod
    @override
    def validate (cls, payload, create = False):
        ti = cls.get_table_info ()
        for field in ti.columns.values ():
            if field.type_name == 'datetime':
                if field.auto_now:
                    payload [field.column] = utcnow ()
                    continue
                if create and field.auto_now_add:
                    payload [field.column] = utcnow ()
                    continue

            if field.column not in payload:
                if create:
                    if field.pk:
                        continue
                    if field.default != NOT_PROVIDED:
                        payload [field.column] = field.default
                        continue
                    if field.null is False:
                        raise ValidationError ('field {} is missing'.format (field.column))
                continue

            value = payload [field.column]
            if isinstance (value, (SQL, D)):
                continue
            if field.null is False and value is None:
                raise ValidationError ('field {} should not be NULL'.format (field.column))
            if field.blank is False and value == '':
                raise ValidationError ('field {} should not be blank'.format (field.column))

            if value is None:
                continue

            if field.type and not isinstance (value, field.type):
                raise ValidationError ('field {} type should be {}'.format (field.column, field.type_name))

            if value == '' and field.null:
                payload [field.column] = value = None
                continue

            if field.choices:
                if isinstance (field.choices [0], (list, tuple)):
                    choices = [item [0] for item in field.choices]
                else:
                    choices = field.choices
                if value not in choices:
                    raise ValidationError ('field {} has invalid value'.format (field.column))

            if field.validators:
                for validate_func in field.validators:
                    validate_func (value)

        for k in payload:
            if k not in ti.columns:
                raise ValidationError ('field {} is not valid field'.format (k))

        return payload

    # collecting table & column infos ----------------------
    @classmethod
    def get_fields (cls):
        if cls._table_info_cache is not None:
            return cls._table_info_cache.columns

        columns = {}
        for field in cls._meta.fields:
            field_type = None
            field_type_name = None
            for ftype, ptype, name in TYPE_MAP:
                if isinstance (field, ftype):
                    field_type = ptype
                    field_type_name = name
                    break

            columns [field.column] = AttrDict (dict (
                column = field.column,
                type = field_type,
                type_name = field_type_name,
                pk = field.primary_key,
                unique = field.unique,
                max_length = field.max_length,
                null = field.null,
                blank = field.blank,
                choices = field.choices,
                help_text = field.help_text,
                validators = field.validators,
                default = field.default,
                name = field.name,
                related_model = field.related_model,
                auto_now_add = field_type_name == 'datetime' and field.auto_now_add or False,
                auto_now = field_type_name == 'datetime' and field.auto_now or False
            ))
        return columns

    @classmethod
    def get_table_info (cls):
        if cls._table_info_cache is None:
            cls._table_info_cache = TableInfo (cls.get_table_name (), cls.get_fields ())
        return cls._table_info_cache

    # basic CRUD ops --------------------------------------
    @classmethod
    def _check_pk (cls, Qs, filters):
        if Qs and not isinstance (Qs [0], _Q):
            pk = list (Qs).pop (0)
            filters [cls.get_table_info ().pk.column] = pk
        return Qs, filters

    @classmethod
    def add (cls, data):
        with was.db (cls._alias) as db:
            return (db.insert (cls)
                        .set (**data))

    @classmethod
    def get (cls, *Qs, **filters):
        Qs, filters = cls._check_pk (Qs, filters)
        with was.db (cls._alias) as db:
            return (db.select (cls)
                        .filter (*Qs, **filters))

    @classmethod
    def cursoring (cls, *Qs, **filters):
        # get with cursoring
        Qs, filters = cls._check_pk (Qs, filters)
        with was.db (cls._alias, cursor = True) as db:
            return (db.select (cls)
                        .filter (*Qs, **filters))

    @classmethod
    def set (cls, data, *Qs, **filters):
        Qs, filters = cls._check_pk (Qs, filters)
        with was.db (cls._alias) as db:
            return (db.update (cls)
                        .set (**data)
                        .filter (*Qs, **filters))

    @classmethod
    def remove (cls, *Qs, **filters):
        Qs, filters = cls._check_pk (Qs, filters)
        with was.db (cls._alias) as db:
            return (db.delete (cls)
                        .filter (*Qs, **filters))

    @classmethod
    def with_ (cls, alias, cte, cursor = False):
        with was.db (cls._alias, cursor = cursor) as db:
            return db.with_ (alias, cte)

    @classmethod
    def fromcte (cls, alias, cursor = False):
        # followed by .with_ ()
        with was.db (cls._alias, cursor = cursor) as db:
            return db.select (alias)

    @classmethod
    def alias (cls, tbl_alias, cursor = False):
        # followed by .join ()
        with was.db (cls._alias, cursor = cursor) as db:
            return db.select (cls, tbl_alias)

    # aliases of was ------------------------------------------
    @classmethod
    def db (cls, *args, **kargs):
        return was.db (cls._alias, *args, **kargs)

    # static methods ------------------------------------------
    @staticmethod
    def utcnow ():
        return utcnow ()

    @staticmethod
    def encodeutc (obj):
        return obj.astimezone (TZ_UTC).strftime ('%Y-%m-%d %H:%M:%S+00')

    @staticmethod
    def decodeutc (s):
        return datetime (*(time.strptime (s, '%Y-%m-%d %H:%M:%S+00')) [:6]).astimezone (TZ_UTC)
