# -*- coding: utf-8 -*-
"""
Custom Django Form Field for pandas.DataFrames.
"""
from django import forms
from django.core.exceptions import ValidationError
from pandas import DataFrame

from django_param.custom_widget.dataframewidget import DataFrameWidget


class DataFrameField(forms.Field):
    """
    Custom Django Form Field for pandas.DataFrames.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
        """
        kwargs["widget"] = DataFrameWidget
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """
        Validate that the value is a DataFrame if the field is required.

        Args:
            value: The value to validate.

        Raises:
            ValidationError: if no DataFrame provided and value is required.
        """
        if not isinstance(value, DataFrame):
            if value in self.empty_values and self.required:
                raise ValidationError(self.error_messages['required'], code='required')

    def run_validators(self, value):
        """
        Run all validators on the field and compile all errors into one error.

        Args:
            value: The value to validate.

        Raises:
            ValidationError: if one or more ValidationErrors is encountered while running validators.
        """
        if not isinstance(value, DataFrame):
            if value in self.empty_values:
                return
            errors = []
            for v in self.validators:
                try:
                    v(value)
                except ValidationError as e:
                    if hasattr(e, 'code') and e.code in self.error_messages:
                        e.message = self.error_messages[e.code]  # noqa: B306
                    errors.extend(e.error_list)
            if errors:
                raise ValidationError(errors)
