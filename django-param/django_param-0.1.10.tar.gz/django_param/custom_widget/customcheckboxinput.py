"""
Custom Checkbox Input Widget.
"""
from django.forms.widgets import CheckboxInput

from django_param.utilities.helpers import is_checkbox


class CustomCheckboxInput(CheckboxInput):
    """
    Custom Checkbox Input Widget.
    """
    template_name = 'django_param/customcheckboxinput/customcheckboxinput_widget.html'
    check_status = None

    def __init__(self, attrs=None, check_status=None):
        """
        Constructor.

        Args:
            attrs: See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.attrs.
            check_status: The default status of the checkbox. If True, the checkbox will be checked. Defaults to None.
        """
        # check_status to control the on/off default status of the checkbox.
        self.check_status = check_status
        super(CustomCheckboxInput, self).__init__(attrs)

    def format_value(self, value):
        """
        Only return the 'value' attribute if value isn't empty.
        """
        return str(value)

    def get_context(self, name, value, attrs):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.get_context.
        """
        context = super(CustomCheckboxInput, self).get_context(name, value, attrs)
        if context['widget']['attrs'] is None:
            context['widget']['attrs'] = {}
        if self.check_status is not None:
            if self.check_status:
                check_on = True
            else:
                check_on = False
        else:
            if bool(value) and value is True:
                check_on = True
            else:
                check_on = False
        context['widget']['attrs']['checked'] = check_on
        return context

    def value_from_datadict(self, data, files, name):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.value_from_datadict.
        """
        value = data.getlist(name)
        # If there are two more data then it's checked.
        if len(value) > 1:
            # ['__checkbox_begin__', '__checkbox_end__']
            if is_checkbox(value[1]):
                return False
            else:
                return True
        else:
            return False
