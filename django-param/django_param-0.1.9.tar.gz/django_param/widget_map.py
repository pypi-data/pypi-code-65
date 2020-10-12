"""
Map of Param Parameters to Django Form Fields and Widgets.
"""
from colorfield.fields import ColorWidget
from django import forms
from django.forms.widgets import NumberInput, Select, SelectMultiple, TextInput
from django_select2.forms import Select2MultipleWidget, Select2Widget
import param

from django_param.custom_field.dataframe import DataFrameField
from django_param.custom_field.tuplefield import NumericTupleField, RangeTupleField, TupleField, XYTupleField
from django_param.custom_widget.customcheckboxinput import CustomCheckboxInput
from django_param.custom_widget.dataframewidget import DataFrameWidget
from django_param.custom_widget.datepicker_widget import DatePickerWidget
from django_param.custom_widget.tuplefield_widget import NumericTupleFieldWidget, RangeTupleFieldWidget, \
    TupleFieldWidget, XYTupleFieldWidget


widget_map = {
    param.Foldername:
        lambda po, p, name: forms.FilePathField(
            initial=po.inspect_value(name) or p.default,
            path=p.search_paths,
            allow_files=False,
            allow_folders=True,
            widget=Select2Widget,
        ),
    param.Boolean:
        lambda po, p, name: forms.BooleanField(
            initial=po.inspect_value(name) or p.default,
            required=False,
            widget=CustomCheckboxInput,
        ),
    # param.Array: ,
    # param.Dynamic: ,
    param.Filename:
        lambda po, p, name: forms.FilePathField(
            initial=po.inspect_value(name) or p.default,
            path=p.search_paths,
            allow_files=True,
            allow_folders=False,
            widget=Select2Widget,
        ),
    param.Dict:
        lambda po, p, name: forms.CharField(
            initial=po.inspect_value(name) or p.default,
            widget_map=TextInput,
        ),
    # param.HookList,
    # param.Action: ,
    param.parameterized.String:
        lambda po, p, name: forms.CharField(
            initial=po.inspect_value(name) or p.default,
            widget=TextInput,
        ),
    param.Magnitude:
        lambda po, p, name: forms.FloatField(
            initial=po.inspect_value(name) or p.default,
            widget=NumberInput(attrs={'step': 0.01, 'max': 1.0, 'min': 0.0}),
        ),
    # param.Composite,
    param.Color:
        lambda po, p, name: forms.CharField(
            initial=po.inspect_value(name) or p.default,
            widget=ColorWidget,
        ),
    param.Number:
        lambda po, p, name: forms.FloatField(
            initial=po.inspect_value(name) or p.default,
            widget=NumberInput(attrs={'step': 0.01, 'max': None if not p.bounds else p.bounds[1],
                                      'min': None if not p.bounds else p.bounds[0]}),
        ),
    param.Date:
        lambda po, p, name: forms.DateTimeField(
            initial=po.inspect_value(name).strftime('%m-%d-%Y %H:%M'),
            input_formats=['%m-%d-%Y %H:%M'],
            widget=DatePickerWidget(
                attrs={
                    'minDate': p.bounds[0].strftime(
                        '%m-%d-%Y') if p.bounds else '0000-01-01',  # start of supported time
                    'maxDate': p.bounds[1].strftime(
                        '%m-%d-%Y') if p.bounds else '9999-12-31',  # end of supported time
                    'format': 'm-d-Y H:i',
                    'formatDate': 'm-d-Y',
                    'timepicker': 'true',
                },
            ),
        ),
    param.CalendarDate:
        lambda po, p, name: forms.DateTimeField(
            initial=po.inspect_value(name).strftime('%m-%d-%Y'),
            input_formats=['%m-%d-%Y'],
            widget=DatePickerWidget(
                attrs={
                    'minDate': p.bounds[0].strftime(
                        '%m-%d-%Y') if p.bounds else '01-01-1900',  # start of supported time
                    'maxDate': p.bounds[1].strftime(
                        '%m-%d-%Y') if p.bounds else '12-31-9999',  # end of supported time
                    'format': 'm-d-Y',
                    'formatDate': 'm-d-Y',
                    'timepicker': 'false',
                },
            ),
        ),
    param.List:
        lambda po, p, name: forms.MultipleChoiceField(
            initial=po.inspect_value(name) or p.default,
            choices=p.get_range().items(),
            widget=SelectMultiple,
        ),
    param.Path:
        lambda po, p, name: forms.FilePathField(
            initial=po.inspect_value(name) or p.default,
            path=p.search_paths,
            allow_files=True,
            allow_folders=True,
            widget=Select2Widget,
        ),
    param.MultiFileSelector:
        lambda po, p, name: forms.MultipleChoiceField(
            initial=po.inspect_value(name),
            choices=p.get_range().items(),
            widget=Select2MultipleWidget,
        ),
    param.ClassSelector:
        lambda po, p, name: forms.ChoiceField(
            initial=po.inspect_value(name) or p.default,
            choices=p.get_range().items(),
            widget=Select,
        ),
    param.FileSelector:
        lambda po, p, name: forms.ChoiceField(
            initial=po.inspect_value(name),
            choices=p.get_range().items(),
            widget=Select2Widget,
        ),
    param.Selector:
        lambda po, p, name: forms.ChoiceField(
            initial=po.inspect_value(name) or p.default,
            choices=p.get_range().items(),
            widget=Select2Widget,
        ),
    param.ListSelector:
        lambda po, p, name: forms.MultipleChoiceField(
            initial=po.inspect_value(name) or p.default,
            choices=p.get_range().items(),
            widget=Select2MultipleWidget,
        ),
    param.ObjectSelector:
        lambda po, p, name: forms.ChoiceField(
            initial=po.inspect_value(name) or p.default,
            choices=p.get_range().items(),
            widget=Select2Widget,
        ),
    # param.Callable,
    param.Tuple:
        lambda po, p, name: TupleField(
            initial=po.inspect_value(name) or p.default,
            required=False,
            fields={name: getattr(po, name)} if getattr(po, name) else {name: p.default},
            widget=TupleFieldWidget,
        ),
    param.NumericTuple:
        lambda po, p, name: NumericTupleField(
            initial=po.inspect_value(name) or p.default,
            required=False,
            fields={name: getattr(po, name)} if getattr(po, name) else {name: p.default},
            widget=NumericTupleFieldWidget,
        ),
    param.XYCoordinates:
        lambda po, p, name: XYTupleField(
            initial=po.inspect_value(name) or p.default,
            required=False,
            fields={name: getattr(po, name)} if getattr(po, name) else {name: p.default},
            widget=XYTupleFieldWidget,
        ),
    param.Range:
        lambda po, p, name: RangeTupleField(
            initial=po.inspect_value(name) or p.default,
            required=False,
            fields={name: getattr(po, name)} if getattr(po, name) else {name: p.default},
            widget=RangeTupleFieldWidget,
        ),
    param.Integer:
        lambda po, p, name: forms.IntegerField(
            initial=po.inspect_value(name) or p.default,
            widget=NumberInput,
        ),
    param.DataFrame:
        lambda po, p, name: DataFrameField(
            initial=getattr(po, name),
            widget=DataFrameWidget(),
        )
}
