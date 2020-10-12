"""
Custom Date Picker Widget.
"""
from datetime import date, datetime

from django import forms


class DatePickerWidget(forms.Widget):
    """
    Custom Date Picker Widget.
    """
    template_name = 'django_param/datepicker/datepicker.html'

    class Media:
        """
        See https://docs.djangoproject.com/en/2.2/topics/forms/media/#assets-as-a-static-definition.
        """
        css = {'all': ('django_param/datepicker/jquery.datetimepicker.min.css',)}
        js = [
            'django_param/datepicker/jquery.datetimepicker.full.js',
        ]

    def get_context(self, name, value, attrs):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.get_context.
        """
        context = dict()
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value': self.format_value(value),
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
        }
        return context

    def value_from_datadict(self, data, files, name):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.value_from_datadict.
        """
        # Convert values into datetimeobject again.
        date_time_str = data[name]
        if ":" in date_time_str:
            date_time_format = '%m-%d-%Y %H:%M'
            date_time_obj = datetime.strptime(date_time_str, date_time_format)
        else:
            date_time_format = '%m-%d-%Y'
            date_time_obj = datetime.strptime(date_time_str, date_time_format).date()
        return date_time_obj

    def format_value(self, value):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.format_value.
        """
        # Convert to datetime to right string to display on the html.
        if isinstance(value, datetime):
            date_time_format = '%m-%d-%Y %H:%M'
            value = value.strftime(date_time_format)
        elif isinstance(value, date):
            date_time_format = '%m-%d-%Y'
            value = value.strftime(date_time_format)
        return value
