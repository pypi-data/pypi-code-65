from __future__ import unicode_literals

import operator
import warnings

from django import forms
from django.utils.functional import Promise
from django.utils.text import capfirst
from django.core import checks, exceptions
from django.utils.encoding import smart_text
from django.utils.deprecation import (
    RemovedInNextVersionWarning as RemovedInDjango20Warning,
)

NOT_IMPL_MSG = 'Method not available on Cassandra model fields'

# The values to use for "blank" in SelectFields. Will be appended to the start
# of most "choices" lists.
BLANK_CHOICE_DASH = [("", "---------"), ]


def value_from_object(self, obj):
    # Taken from django.db.models.fields.__init__
    return getattr(obj, self.attname)


def value_to_string(self, obj):
    # Taken from django.db.models.fields.__init__
    return smart_text(self.value_from_object(obj))


def get_attname(self):
    # Taken from django.db.models.fields.__init__
    return self.name


def get_cache_name(self):
    # Taken from django.db.models.fields.__init__
    return '_%s_cache' % self.name


def get_attname_column(self):
    # Taken from django.db.models.fields.__init__
    attname = self.get_attname()
    column = self.db_column or attname
    return attname, column


def pre_save(self, model_instance, add):
    # Taken from django.db.models.fields.__init__
    return getattr(model_instance, self.attname)


def get_prep_value(self, value):
    # Taken from django.db.models.fields.__init__
    if isinstance(value, Promise):
        value = value._proxy___cast()
    return value


def get_db_prep_value(self, value, connection, prepared=False):
    # Taken from django.db.models.fields.__init__
    if not prepared:
        value = self.get_prep_value(value)
    return value


def get_db_prep_save(self, value, connection):
    # Taken from django.db.models.fields.__init__
    return self.get_db_prep_value(value, connection=connection,
                                  prepared=False)


def get_db_converters(self, *args, **kwargs):
    # Taken from django.db.models.fields.__init__
    return []


def get_internal_type(self):
    # Taken from django.db.models.fields.__init__
    return self.__class__.__name__


def save_form_data(self, instance, data):
    # Taken from django.db.models.fields.__init__
    if data == '':
        data = None
    setattr(instance, self.name, data)


def get_filter_kwargs_for_object(self, obj):
    # Taken from django.db.models.fields.__init__
    return {self.name: getattr(obj, self.attname)}


def formfield(self, form_class=None, choices_form_class=None, **kwargs):
    # Taken from django.db.models.fields.__init__
    defaults = {'required': not self.blank,
                'label': capfirst(self.verbose_name),
                'help_text': self.help_text}
    if self.has_default:
        if callable(self.default):
            defaults['initial'] = self.default
            defaults['show_hidden_initial'] = True
        else:
            defaults['initial'] = self.get_default()
    if self.choices:
        # Fields with choices get special treatment.
        include_blank = (self.blank or
                         not (self.has_default or 'initial' in kwargs))
        defaults['choices'] = self.get_choices(include_blank=include_blank)
        defaults['coerce'] = self.to_python
        if self.null:
            defaults['empty_value'] = None
        if choices_form_class is not None:
            form_class = choices_form_class
        else:
            form_class = forms.TypedChoiceField
        # Many of the subclass-specific formfield arguments (min_value,
        # max_value) don't apply for choice fields, so be sure to only pass
        # the values that TypedChoiceField will understand.
        for k in list(kwargs):
            if k not in ('coerce', 'empty_value', 'choices', 'required',
                         'widget', 'label', 'initial', 'help_text',
                         'error_messages', 'show_hidden_initial'):
                del kwargs[k]
    defaults.update(kwargs)

    # Decide the form class
    if form_class is None:
        if self.__class__.__name__ in ('Boolean',):
            form_class = forms.BooleanField
        elif self.__class__.__name__ in ('DateTime',):
            form_class = forms.DateTimeField
        elif self.__class__.__name__ in ('Date', ):
            form_class = forms.DateField
        elif self.__class__.__name__ in ('Time',):
            form_class = forms.TimeField
        else:
            form_class = forms.CharField

    return form_class(**defaults)


def check(self, **kwargs):
    # Taken from django.db.models.fields.__init__
    # Modified to support cqlengine
    errors = []
    errors.extend(self._check_field_name())
    errors.extend(self._check_db_index())
    return errors


def _check_db_index(self):
    # Taken from django.db.models.fields.__init__
    if self.db_index not in (None, True, False):
        return [
            checks.Error(
                "'db_index' must be None, True or False.",
                hint=None,
                obj=self,
                id='fields.E006',
            )
        ]
    else:
        return []


def _check_field_name(self):
    # Taken from django.db.models.fields.__init__
    if self.name.endswith('_'):
        return [
            checks.Error(
                'Field names must not end with an underscore.',
                hint=None,
                obj=self,
                id='fields.E001',
            )
        ]
    elif '__' in self.name:
        return [
            checks.Error(
                'Field names must not contain "__".',
                hint=None,
                obj=self,
                id='fields.E002',
            )
        ]
    elif self.name == 'pk':
        return [
            checks.Error(
                "'pk' is a reserved word that cannot be used as a field name.",
                hint=None,
                obj=self,
                id='fields.E003',
            )
        ]
    else:
        return []


def run_validators(self, value):
    # Taken from django.db.models.fields.__init__
    if value in self.empty_values:
        return

    errors = []
    for v in self.validators:
        try:
            v(value)
        except exceptions.ValidationError as e:
            if hasattr(e, 'code') and e.code in self.error_messages:
                e.message = self.error_messages[e.code]
            errors.extend(e.error_list)

    if errors:
        raise exceptions.ValidationError(errors)


def clean(self, value, model_instance):
    # Taken from django.db.models.fields.__init__
    # Modified to support cqlengine
    value = self.to_python(value)
    # This is python-driver validate method not Django
    self.validate(value=value)
    self.run_validators(value)
    return value


def get_pk_value_on_save(self, instance):
    # Taken from django.db.models.fields.__init__
    if self.default:
        return self.get_default()
    return None


def get_choices_default(self):
    # Taken from django.db.models.fields.__init__
    return self.get_choices()


@property
def rel(self):
    # Taken from django.db.models.fields.__init__
    warnings.warn(
        "Usage of field.rel has been deprecated. Use field.remote_field instead.",
        RemovedInDjango20Warning, 2)
    return self.remote_field


def db_parameters(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def db_type(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def db_type_suffix(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def get_prep_lookup(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def get_col(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def get_db_prep_lookup(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def select_format(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def deconstruct(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)


def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
    """
    Return choices with a default blank choices included, for use as <select> choices for this field.
    """
    choices = list(self.choices)
    if include_blank:
        blank_defined = any(choice in ('', None) for choice, _ in self.flatchoices)
        if not blank_defined:
            choices = blank_choice + choices

    return choices


def set_attributes_from_name(self, *args, **kwargs):
    raise NotImplementedError(NOT_IMPL_MSG)
