"""
Custom Django Form that can be defined using a param.Parameterized object.
"""
from datetime import date, datetime

from django import forms
from pandas import DataFrame
import param

from django_param.utilities.helpers import clean_data, get_dataframe_name, is_checkbox, remove_item_tuple, \
    update_item_tuple
from django_param.widget_map import widget_map as default_widget_map


class ParamForm(forms.Form):
    """
    Custom Django Form that can be defined using a param.Parameterized object.
    """
    read_only = None
    cleaned_data = ""
    _param = None
    _error_key_list = []
    _widget_map = default_widget_map

    @property
    def param(self):
        """
        Getter for underlying param.Parameter object.
        """
        return self._param

    @property
    def widget_map(self):
        """
        Getter for underlying dictionary used to map param.Parameters to Django Fields/Widgets.
        """
        return self._widget_map

    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            param (param.Parameterized): The Parameterized object to use to define the form.
            read_only (bool): Render form as read-only (not editable).
            widget_map (dict): A dictionary containing custom mapping(s) of param.Parameters to Django Fields/Widgets.
            *args: See https://docs.djangoproject.com/en/2.2/ref/forms/api/#django.forms.Form.
            **kwargs: See https://docs.djangoproject.com/en/2.2/ref/forms/api/#django.forms.Form.
        """
        param_class = kwargs.pop('param', None)
        if param_class is None:
            raise KeyError('Keyword argument param is required.')
        if not isinstance(param_class, param.Parameterized):
            raise ValueError(f'{param_class} must be an instance of param.Parameterized.')
        self._param = param_class

        read_only = kwargs.pop('read_only', None)
        if read_only:
            self.read_only = read_only

        custom_widget_map = kwargs.pop('widget_map', None)
        if custom_widget_map:
            self._widget_map = custom_widget_map
        super().__init__(*args, **kwargs)
        self._generate_form_fields()

    def _add_error(self, key, message):
        """
        Only add error once for each parameter to avoid duplicate.
        """
        if key not in self._error_key_list:
            self._error_key_list.append(key)
            self.add_error(key, str(message))

    def _set_and_validate_data(self, data):
        """
        Custom validation method.
        """
        # To handle dataframe case
        dataframe_key_list = []

        for key in data.keys():
            if key != 'csrfmiddlewaretoken':
                if get_dataframe_name(key):
                    variable_name, dataframe_name = get_dataframe_name(key)
                    dataframe_key_list.append(variable_name)
                else:
                    self._set_and_validate_data_name(data, key)
        if dataframe_key_list:
            self._set_and_validate_dataframe(data, dataframe_key_list, dataframe_name)

    def _set_and_validate_dataframe(self, data, data_list, dataframe_name):
        """
        Custom validation method.
        """
        # Handle Dataframe case
        data_dict = {}
        for key in data_list:
            data_dict[key] = data.getlist(key + "___" + dataframe_name + "__")
        value = DataFrame.from_dict(data_dict)
        # Update param
        self.param.set_param(dataframe_name, value)

    def _set_and_validate_data_name(self, data, name):
        """
        Custom validation method.
        """
        # Find out if it is dataframe
        is_dict = False
        if isinstance(self.param.params()[name], (param.List, param.ListSelector)):
            is_dict = True
        value_temp = data.getlist(name)

        # Clean up data
        if len(value_temp) > 1:
            value = clean_data(value_temp, is_dict=is_dict)
        else:
            value = clean_data(data.get(name), is_dict=is_dict)

        # Convert to datetime object if neccessary
        if isinstance(self.param.inspect_value(name), (date, datetime)):
            date_time_str = data[name]
            if ":" in date_time_str:
                date_time_format = '%m-%d-%Y %H:%M'
                value = datetime.strptime(date_time_str, date_time_format)
            else:
                date_time_format = '%m-%d-%Y'
                value = datetime.strptime(date_time_str, date_time_format).date()

        if isinstance(self.param.params()[name], param.Boolean):
            if is_checkbox(value[1]):
                value = False
            else:
                value = True

        if isinstance(self.param.params()[name], param.Tuple):
            try:
                for i in range(len(value)):
                    if is_checkbox(value[i]):
                        # there is no value in between, the check box is off
                        if is_checkbox(value[i + 1]):
                            value = update_item_tuple(value, i, False)
                            value = remove_item_tuple(value, i + 1)
                        #
                        else:
                            value = update_item_tuple(value, i, True)
                            value = remove_item_tuple(value, i + 1)
                            value = remove_item_tuple(value, i + 1)
            except IndexError:
                pass

        try:
            # Update param
            self.param.set_param(name, value)
        except ValueError as e:
            self._add_error(name, e)

    def _generate_form_fields(self):
        """
        Create a Django form from a Parameterized object.

        Returns:
            Form: a Django form with fields matching the parameters of the given parameterized object.
        """
        params = list(filter(lambda x: (x.precedence is None or x.precedence >= 0) and not x.constant,
                             self.param.params().values()))
        for p in sorted(params, key=lambda p: p.precedence or 9999):
            # TODO: Pass p.__dict__ as second argument instead of arbitrary
            p_name = p.name

            # Preserve param tuple type.
            if self.data:
                if isinstance(getattr(self.param, p.name), tuple):
                    p.default = tuple(self.data.getlist(p.name))

            # Preserve initial options for Selector
            if isinstance(self.param.params()[p_name], (param.FileSelector, param.MultiFileSelector)):
                p.default = ""

            self.fields[p_name] = self.widget_map[type(p)](self.param, p, p.name)
            self.fields[p_name].label = p.name.replace("_", " ").title()
            if self.read_only is None:
                widget_attribute = {'class': 'form-control'}
            else:
                # TODO: Should this be readonly instead of disable?
                widget_attribute = {'class': 'form-control', 'disabled': self.read_only}
            self.fields[p_name].widget.attrs.update(widget_attribute)
            self.fields[p_name].required = not self.param.params()[p_name].allow_None
            self.fields[p_name].disabled = self.param.params()[p_name].constant
            self.fields[p_name].help_text = self.param.params()[p_name].doc
        # self.fields = self.base_fields

    def as_param(self):
        """
        Clean form and return underlying param.Parameterized object.
        """
        self._clean()
        return self.param

    def _clean(self):
        """
        Custom clean method called only when retrieving the param object.
        """
        self.cleaned_data = super().clean()
        # Use bound data to set the value if we both have bound and initial data.
        if self.is_bound and self.initial:
            self._set_and_validate_data(self.data)
            return
        else:
            # Set values according to bound data
            if self.is_bound:
                self._set_and_validate_data(self.data)
                return
            # Set values according to initial data
            if self.initial:
                self._set_and_validate_data(self.initial)
                return
