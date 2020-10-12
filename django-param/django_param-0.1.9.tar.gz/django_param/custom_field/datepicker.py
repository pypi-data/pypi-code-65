"""
Custom DatePicker Django Field.
"""
from django.forms import DateTimeInput

from django_param.custom_widget.datepicker_widget import DatePickerWidget


class DateTimePicker(DateTimeInput):
    """
    Custom DatePicker Django Field.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/fields/#core-field-arguments
        """
        kwargs["widget"] = DatePickerWidget
        super().__init__(*args, **kwargs)
