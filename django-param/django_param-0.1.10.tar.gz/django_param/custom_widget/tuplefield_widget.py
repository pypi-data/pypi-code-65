"""
Custom Django Widgets for param.Tuple derived Parameters.
"""
import pickle

from django import forms

from django_param.custom_widget.customcheckboxinput import CustomCheckboxInput
from django_param.utilities.helpers import is_checkbox, remove_item_tuple, update_item_tuple


class TupleFieldWidget(forms.widgets.MultiWidget):
    """
    Custom Django Widget for param.Tuple Parameters.
    """
    def __init__(self, attrs=None):
        """
        Constructor.

        Args:
            attrs: See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#widget
        """
        widgets = [forms.TextInput()]
        super(TupleFieldWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        """
        See: https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.MultiWidget.decompress.
        """
        if not isinstance(value, tuple):
            if value:
                return pickle.loads(value)
            else:
                return ['', '']
        else:
            return value

    def custom_get_context(self, name, value, attrs, context, **kwargs):
        """
        Extension of get_context.
        """
        xy = kwargs.get('xy', False)
        range_option = kwargs.get('range_option', False)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', None)
        id_ = final_attrs.get('id')
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type
            widget_name = name
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs['id'] = '%s_%s' % (id_, i)
            else:
                widget_attrs = final_attrs

            # Set step to any
            widget_attrs['step'] = "any"

            # Add label for xy coordinates
            widget_handler = widget.get_context(widget_name, widget_value, widget_attrs)['widget']
            if i == 0:
                if xy:
                    widget_handler['label'] = "X"
                if range_option:
                    widget_handler['label'] = "Min"
            else:
                if xy:
                    widget_handler['label'] = "Y"
                if range_option:
                    widget_handler['label'] = "Max"
            subwidgets.append(widget_handler)
        context['widget']['subwidgets'] = subwidgets
        return context

    def get_context(self, name, value, attrs):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.get_context.
        """
        context = forms.Widget.get_context(self, name, value, attrs)
        self.widgets = []
        # Update number of widgets
        try:
            for i in range(len(value)):
                # Find out if we should have the checkbox on or off
                check_status = True
                if isinstance(value[i], (float, int)):
                    self.widgets.append(forms.NumberInput())
                else:
                    if is_checkbox(value[i]):
                        # there is no value in between, the check box is off
                        if is_checkbox(value[i + 1]):
                            value = update_item_tuple(value, i, False)
                            value = remove_item_tuple(value, i + 1)
                            check_status = False
                        #
                        else:
                            value = update_item_tuple(value, i, True)
                            value = remove_item_tuple(value, i + 1)
                            value = remove_item_tuple(value, i + 1)
                            check_status = True

                        self.widgets.append(CustomCheckboxInput(check_status=check_status))
                    else:
                        self.widgets.append(forms.TextInput())
        except IndexError:
            pass

        context = self.custom_get_context(name, value, attrs, context)
        return context

    def value_from_datadict(self, data, files, name):
        """
        See: https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.value_from_datadict.
        """
        # Override this method since we use one name for all the widgets.
        values = data.getlist(name)
        return values


class NumericTupleFieldWidget(TupleFieldWidget):
    """
    Custom Django Widget for param.NumericTuple Parameters.
    """
    def get_context(self, name, value, attrs):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.get_context.
        """
        context = forms.Widget.get_context(self, name, value, attrs)
        self.widgets = []
        # Update number of widgets
        for _ in range(len(value)):
            self.widgets.append(forms.NumberInput())

        context = self.custom_get_context(name, value, attrs, context)
        return context


class XYTupleFieldWidget(TupleFieldWidget):
    """
    Custom Django Widget for param.XYCoordinates Parameters.
    """
    def get_context(self, name, value, attrs):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.get_context.
        """
        context = forms.Widget.get_context(self, name, value, attrs)
        self.widgets = []
        # Update number of widgets
        for _ in range(2):
            self.widgets.append(XYNumberInput())

        context = self.custom_get_context(name, value, attrs, context, xy=True)
        return context


class RangeTupleFieldWidget(TupleFieldWidget):
    """
    Custom Django Widget for param.Range Parameters.
    """
    def get_context(self, name, value, attrs):
        """
        See https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#django.forms.Widget.get_context.
        """
        context = forms.Widget.get_context(self, name, value, attrs)
        self.widgets = []
        # Update number of widgets
        for _ in range(2):
            self.widgets.append(XYNumberInput())

        context = self.custom_get_context(name, value, attrs, context, range_option=True)
        return context


class XYNumberInput(forms.NumberInput):
    """
    Custom Django Widget for a pair of Number inputs.
    """
    # Template works for both range and xy coordinates
    template_name = 'django_param/tuplefield/xytuplefield.html'
