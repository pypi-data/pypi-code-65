class ServiceBase:
    debug = False


# integrating django model ----------------------------------
try:
    from django.core.exceptions import ValidationError
    from django.db import models as types

except ImportError:
    class Service (ServiceBase):
        pass

else:
    import datetime
    import uuid
    from rs4.attrdict import AttrDict

    TYPE_MAP = [
        (types.CharField, str, 'string'),
        ((types.IntegerField, types.AutoField), int, 'integer'),
        (types.FloatField, float, 'float'),
        (types.BooleanField, bool, 'boolean'),
        (types.DateTimeField, datetime.datetime, 'datetime'),
        (types.DateField, datetime.date, 'date'),
        (types.TimeField, datetime.time, 'time'),
        (types.UUIDField, uuid.UUID, 'uuid'),
    ]

    class TableInfo:
        def __init__ (self, name, columns):
            self.name = name
            self.columns = columns
            self.pk = None

            for field in self.columns.values ():
                if field.pk:
                    self.pk = field
                    break


    class Service (ServiceBase):
        ValidationError = ValidationError
        table_info_cache = {}

        @classmethod
        def get_table_info (cls, model):
            name = cls.get_table_name (model)
            if not cls.debug and name in cls.table_info_cache:
                return cls.table_info_cache [name]
            cls.table_info_cache [name] = TableInfo (name, cls.get_table_columns (model))
            return cls.table_info_cache [name]

        @classmethod
        def get_table_name (cls, model):
            return model._meta.db_table

        @classmethod
        def get_table_columns (cls, model):
            columns = {}
            for field in model._meta.fields:
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
                    type_Name = field_type_name,
                    pk = field.primary_key,
                    unique = field.unique,
                    max_length = field.max_length,
                    null = field.null,
                    blank = field.blank,
                    choices = field.choices,
                    help_text = field.help_text,
                    validators = field.validators,
                ))
            return columns

        @classmethod
        def validate (cls, model, payload, null_check = False):
            ti = cls.get_table_info (model)
            for field in ti.columns.values ():
                if field.column not in payload:
                    if null_check and field.null is False:
                        raise ValidationError ('field {} is missing'.format (field.column))
                    continue

                value = payload [field.column]
                if field.null is False and value is None:
                    raise ValidationError ('field {} should not be NULL'.format (field.column))
                if field.blank is False and value == '':
                    raise ValidationError ('field {} should not be blank'.format (field.column))

                if value is None:
                    return

                if field.type and not isinstance (value, field.type):
                    raise ValidationError ('field {} type should be {}'.format (field.column, field.type_name))

                if value == '' and field.null:
                    payload [field.column] = value = None
                    return

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
