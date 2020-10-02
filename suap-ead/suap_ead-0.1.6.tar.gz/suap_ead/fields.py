from django.db.models import CharField
from django.db.models import ForeignKey, CASCADE


nullable = {'null': True, 'blank': True}
nullable_phone = {'null': True, 'blank': True, 'help_text': '(00) 00000-0000', 'max_length': 15}


class StringField(CharField):
    def __init__(self, max_length=255, *args, **kwargs):
        kwargs['max_length'] = max_length
        super().__init__(*args, **kwargs)


class NullStringField(StringField):
    def __init__(self, max_length=255, null=True, blank=True, *args, **kwargs):
        kwargs['max_length'] = max_length
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)


class FK(ForeignKey):

    def __init__(self, verbose_name, to, on_delete=CASCADE, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):
        super().__init__(
            to,
            on_delete=on_delete,
            related_name=related_name,
            related_query_name=related_query_name,
            limit_choices_to=limit_choices_to,
            parent_link=parent_link,
            to_field=to_field,
            db_constraint=db_constraint,
            verbose_name=verbose_name,
            **kwargs)


class NullFK(ForeignKey):

    def __init__(self, verbose_name, to, on_delete=CASCADE, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):
        if 'null' in kwargs:
            kwargs.pop('null')
        if 'blank' in kwargs:
            kwargs.pop('blank')
        super().__init__(
            to,
            on_delete=on_delete,
            related_name=related_name,
            related_query_name=related_query_name,
            limit_choices_to=limit_choices_to,
            parent_link=parent_link,
            to_field=to_field,
            db_constraint=db_constraint,
            verbose_name=verbose_name,
            null=True,
            blank=True,
            **kwargs)
