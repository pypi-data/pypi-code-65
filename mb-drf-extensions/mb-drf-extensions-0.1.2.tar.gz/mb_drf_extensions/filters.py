from uuid import UUID

from django.forms import CharField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import filters

__all__ = [
    'CharListFilter',
    'UUIDListFilter',
    *filters.__all__,
]


class UUIDListField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid list of UUID.'),
    }

    def __init__(self, separator=',', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.separator = separator

    def prepare_value(self, value):
        if isinstance(value, list):
            return self.separator.join(
                v.hex for
                v in value if isinstance(v, UUID)
            )
        return value

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return None

        if not isinstance(value, list):
            try:
                value = [
                    UUID(v.strip()) for
                    v in value.split(self.separator) if
                    v.strip()
                ]
            except ValueError:
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid'
                )
        return value


class CharListField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid list of Text.'),
    }

    def __init__(self, separator=',', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.separator = separator

    def prepare_value(self, value):
        if isinstance(value, list):
            return self.separator.join([
                v for v in value if
                v.strip() and self.separator not in v
            ])
        return value

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return None

        if not isinstance(value, list):
            try:
                value = [
                    v.strip() for
                    v in value.split(self.separator) if
                    v.strip()
                ]
            except ValueError:
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid'
                )
        return value


class UUIDListFilter(filters.Filter):
    field_class = UUIDListField


class CharListFilter(filters.Filter):
    field_class = CharListField
