# -*- coding: utf-8 -*-
"""
Custom Django Form Fields to handle Param.Tuple parameters.
"""
import pickle

from django import forms

from django_param.custom_widget.tuplefield_widget import NumericTupleFieldWidget, RangeTupleFieldWidget, \
    TupleFieldWidget, XYTupleFieldWidget


class TupleField(forms.MultiValueField):
    """
    Custom Django Form Field to handle Param.Tuple parameters.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
        """
        kwargs["widget"] = TupleFieldWidget
        fields = []
        raw_fields = kwargs.pop('fields', None)
        for _, value in raw_fields.items():
            for i in range(len(value)):
                fields.append(forms.CharField(initial=value[i]))
        super().__init__(fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        """
        See: https://docs.djangoproject.com/en/2.2/ref/forms/fields/#django.forms.MultiValueField.compress.

        Args:
            data_list (list): Data to be compressed.

        Returns:
            various: Compressed data.
        """
        return pickle.dumps(self.initial)


class NumericTupleField(forms.MultiValueField):
    """
    Custom Django Form Field to handle Param.NumericTuple parameters.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
        """
        kwargs["widget"] = NumericTupleFieldWidget
        fields = []
        raw_fields = kwargs.pop('fields', None)
        for _, value in raw_fields.items():
            for _ in range(len(value)):
                fields.append(forms.CharField())
        super().__init__(fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        """
        See: https://docs.djangoproject.com/en/2.2/ref/forms/fields/#django.forms.MultiValueField.compress.

        Args:
            data_list (list): Data to be compressed.

        Returns:
            various: Compressed data.
        """
        return pickle.dumps(self.initial)


class XYTupleField(forms.MultiValueField):
    """
    Custom Django Form Field to handle Param.XYCoordinate parameters.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
        """
        kwargs["widget"] = XYTupleFieldWidget
        fields = []
        raw_fields = kwargs.pop('fields', None)
        for _, value in raw_fields.items():
            for _ in range(len(value)):
                fields.append(forms.CharField())
        super().__init__(fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        """
        See: https://docs.djangoproject.com/en/2.2/ref/forms/fields/#django.forms.MultiValueField.compress.

        Args:
            data_list (list): Data to be compressed.

        Returns:
            various: Compressed data.
        """
        return pickle.dumps(self.initial)


class RangeTupleField(forms.MultiValueField):
    """
    Custom Django Form Field to handle Param.Range parameters.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
        """
        kwargs["widget"] = RangeTupleFieldWidget
        fields = []
        raw_fields = kwargs.pop('fields', None)
        for _, value in raw_fields.items():
            for _ in range(len(value)):
                fields.append(forms.CharField())
        super().__init__(fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        """
        See: https://docs.djangoproject.com/en/2.2/ref/forms/fields/#django.forms.MultiValueField.compress.

        Args:
            data_list (list): Data to be compressed.

        Returns:
            various: Compressed data.
        """
        return pickle.dumps(self.initial)
