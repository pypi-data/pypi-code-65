import param
from django_param.forms import ParamForm
import pytest
import datetime as dt
import pandas as pd
from django.http import QueryDict


class MyParam(param.Parameterized):
    probability = param.Number(0.5, bounds=(0, 1), doc="Probability that...")
    test_string = param.String(default="test string", doc="Probability that...")


class MyParamString(param.Parameterized):
    param_string = param.String(default="hello world!", doc="Your String")


class MyParamXYCoordinates(param.Parameterized):
    xy_coordinates = param.XYCoordinates(default=(-111.65, 40.23))


class MyParamDataFrame(param.Parameterized):
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    dataset = param.DataFrame(df)


class MyParamColor(param.Parameterized):
    color = param.Color(default='#FFFFFF')


class MyParamSelector(param.Parameterized):
    selector = param.Selector(default='red', objects=["red", "yellow", "green", "blue"])


class MyParamListSelector(param.Parameterized):
    list_selector = param.ListSelector(objects=["red", "yellow", "green", "blue"])


class MyParamSelectString(param.Parameterized):
    select_string = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])


class MyParamDate(param.Parameterized):
    date = param.CalendarDate(dt.date(2020, 1, 1))


class MyParamDateTime(param.Parameterized):
    datetime = param.Date(dt.datetime(2020, 1, 1, 0, 0, 0), bounds=(dt.datetime(2017, 1, 1, 0, 0, 0),
                                                                    dt.datetime(2021, 1, 1, 0, 0, 0)))


class MyParamBoolean(param.Parameterized):
    boolean = param.Boolean(True, doc="A sample Boolean parameter", allow_None=True)


class MyParamMagnitude(param.Parameterized):
    magnitude = param.Magnitude(default=0.9)


class MyParamNumber(param.Parameterized):
    number = param.Number(49, bounds=(0, 100), doc="Any Number between 0 to 100")


class MyParamRange(param.Parameterized):
    my_ranges = param.Range(default=(-50, 50))


class MyParamTuple(param.Parameterized):
    my_tuples = param.Tuple(default=("test", 50, 'Aquaveo', 100, "Hello", False), allow_None=True)


class MyParamNumericTuple(param.Parameterized):
    my_numeric_tuples = param.NumericTuple(default=(1, 2, 3))


class MyParamFileSelector(param.Parameterized):
    single_file = param.FileSelector(path='*', precedence=0.5)


class MyParamMultiFileSelector(param.Parameterized):
    multiple_files = param.MultiFileSelector(path='*', precedence=0.5)


class TestForm:
    def test_form_empty(self):
        with pytest.raises(KeyError, match="Keyword argument param is required."):
            ParamForm()

    def test_form_invalid_param(self):
        with pytest.raises(ValueError, match="test must be an instance of param.Parameterized."):
            ParamForm(param="test")

    def test_form_no_bound(self):
        test_param = MyParam()

        # Test read-only
        no_bound_no_initial = ParamForm(param=test_param, read_only=True)
        no_bound_no_initial.clean()
        expected_html = '<tr><th><label for="id_probability">Probability:</label></th><td><input type="number"' \
                        ' name="probability" value="0.5" step="0.01" max="1" min="0" class="form-control"' \
                        ' disabled required id="id_probability"><br><span class="helptext">Probability' \
                        ' that...</span></td></tr>\n<tr><th><label for="id_test_string">Test String:</label>' \
                        '</th><td><input type="text" name="test_string" value="test string" class="form-control"' \
                        ' disabled required id="id_test_string"><br><span class="helptext">Probability that...</span>' \
                        '</td></tr>'
        # Check results. No bound has no data for validation so is_valid is false
        str(no_bound_no_initial)
        assert str(no_bound_no_initial) == expected_html
        assert no_bound_no_initial.is_bound is False
        assert no_bound_no_initial.is_valid() is False
        assert no_bound_no_initial.errors == {}

    def test_param_boolean(self):
        my_param = MyParamBoolean()
        request_data = QueryDict('', mutable=True)
        request_data = QueryDict('boolean=__checkbox_begin__&boolean=True&boolean=__checkbox_end__', mutable=True)
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('boolean') is True
        assert form.is_valid() is True

    def test_param_boolean_false(self):
        my_param = MyParamBoolean()
        request_data = QueryDict('boolean=__checkbox_begin__&boolean=__checkbox_end__', mutable=True)
        form = ParamForm(request_data, param=my_param)
        assert form.is_valid() is True

        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('boolean') is False

    def test_param_string(self):
        my_param = MyParamString()
        request_data = QueryDict('', mutable=True)
        request_data.update({'param_string': 'test string'})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        expected_html = '<tr><th><label for="id_param_string">Param String:</label></th><td><input type="text"' \
                        ' name="param_string" value="test string" class="form-control" required' \
                        ' id="id_param_string"><br><span class="helptext">Your String</span></td></tr>'

        # Check result
        assert the_param.inspect_value('param_string') == 'test string'
        assert str(form) == expected_html
        assert form.is_valid() is True

    def test_param_color(self):
        my_param = MyParamColor()
        request_data = QueryDict('', mutable=True)
        request_data.update({'csrfmiddlewaretoken': 'testcrsf', 'color': 'FFFFFF'})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        expected_html = '<tr><th><label for="id_color">Color:</label></th><td><input type="text"\n id="id_color"\n' \
                        ' class="form-control colorfield_field jscolor"\n name="color"\n value="FFFFFF"\n' \
                        ' placeholder="FFFFFF"\n data-jscolor="{hash:true,width:225,height:150,required:true}"\n' \
                        ' required /></td></tr>'
        # Check result
        assert str(form) == expected_html
        assert the_param.inspect_value('color') == 'FFFFFF'
        assert form.is_valid() is True

    def test_param_dataframe(self):
        my_param = MyParamDataFrame()
        request_data = QueryDict('', mutable=True)
        d_after = {'col1___dataset__': [5, 6], 'col2___dataset__': [7, 8]}
        request_data.update(d_after)

        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        expected_html = '<tr><th><label for="id_dataset">Dataset:</label></th><td><!--<button onclick="">' \
                        'Load Dataframe</button>-->\n\n\n<!--<input name="feature-id" value="" hidden>-->\n' \
                        '<!--<h6 class="title">dataset</h6>-->\n<div class="row" >\n' \
                        '    <div class="col-sm-6 pop-up-col table-col">\n        <a id="spatial-dataset-add-row-btn"' \
                        ' class="btn btn-xs btn-default table-btn pull-right" title="Add row">\n' \
                        '            <span class="glyphicon glyphicon-plus"></span>\n        </a>\n' \
                        '        <a id="spatial-dataset-remove-row-btn" class="btn btn-xs btn-default' \
                        ' table-btn pull-right" title="Remove row">\n            <span class="glyphicon' \
                        ' glyphicon-minus"></span>\n        </a>\n        <a id="spatial-dataset-clear-table-btn"' \
                        ' class="btn btn-xs btn-default table-btn pull-right" title="Clear table">\n' \
                        '            <span class="glyphicon glyphicon-trash"></span>\n        </a>\n ' \
                        '       <a id="spatial-dataset-copy-table-btn" class="btn btn-xs btn-default table-btn' \
                        ' pull-right" title="Copy">\n            <span class="glyphicon glyphicon-copy"></span>\n ' \
                        '       </a>\n        <table id="spatial-dataset-table"\n          ' \
                        '     class="table table-bordered table-striped table-hover spatial-data-table"\n     ' \
                        '          data-max-rows="">\n            <thead>\n                <tr>\n                  ' \
                        '  \n                    <th>col1</th>\n                    \n                  ' \
                        '  <th>col2</th>\n                    \n                </tr>\n            </thead>\n     ' \
                        '       <tbody>\n                \n                <tr>\n                    \n              ' \
                        '      <td>\n                        <input type="text"\n                               ' \
                        'class="form-field"\n                               name="col1___dataset__"\n                ' \
                        '               value="[5, 6]"\n                               >\n                    </td>\n' \
                        '                    \n                    <td>\n                        <input type="text"\n' \
                        '                               class="form-field"\n                               ' \
                        'name="col2___dataset__"\n                               value="[7, 8]"\n                   ' \
                        '            >\n                    </td>\n                    \n                </tr>\n     ' \
                        '           \n            </tbody>\n        </table>\n    </div>\n ' \
                        '   <div class="col-sm-6 pop-up-col">\n        <div id="spatial-dataset-plot"></div>\n ' \
                        '   </div>\n</div></td></tr>'
        # Check result
        assert str(form) == expected_html
        assert the_param.inspect_value('dataset').values[0][0] == [5, 6]
        assert the_param.inspect_value('dataset').values[0][1] == [7, 8]
        assert form.is_valid() is True

    def test_param_selector(self):
        my_param = MyParamSelector()
        request_data = QueryDict('', mutable=True)
        request_data.update({'selector': 'red'})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('selector') == 'red'
        assert form.is_valid() is True

    def test_param_list_selector(self):
        my_param = MyParamListSelector()
        request_data = QueryDict('list_selector=red&list_selector=green', mutable=True)
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('list_selector') == ['red', 'green']
        assert form.is_valid() is True

    def test_date(self):
        my_param = MyParamDate()
        request_data = QueryDict('', mutable=True)
        request_data.update({'date': "01-01-2020"})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('date') == dt.date(2020, 1, 1)

        assert form.is_valid() is True

    def test_datetime(self):
        my_param = MyParamDateTime()
        request_data = QueryDict('', mutable=True)
        request_data.update({'datetime': "01-01-2020 10:10"})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('datetime') == dt.datetime(2020, 1, 1, 10, 10)
        assert form.is_valid() is True

    def test_xycoordinates(self):
        my_param = MyParamXYCoordinates()
        request_data = QueryDict('', mutable=True)
        request_data.update({'xy_coordinates': ['-100', '100']})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('xy_coordinates') == (-100, 100)
        assert form.is_valid() is True

    def test_range(self):
        my_param = MyParamRange()
        request_data = QueryDict('', mutable=True)
        request_data.update({'my_ranges': ['-100', '100']})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('my_ranges') == (-100, 100)
        assert form.is_valid() is True

    def test_tuples_double(self):
        my_param = MyParamTuple()
        request_data = QueryDict('', mutable=True)
        request_data.update({'my_tuples': ['-100', '100', 'Aquaveo', 'Test', '1', '__checkbox_begin__', 'False',
                                           '__checkbox_end__']})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('my_tuples') == (-100, 100, 'Aquaveo', 'Test', 1, True)
        assert form.is_valid() is True

    def test_tuples(self):
        my_param = MyParamTuple()
        request_data = QueryDict('', mutable=True)
        request_data.update({'my_tuples': ['-100', '100', 'Aquaveo', 'Test', '1', '__checkbox_begin__',
                                           '__checkbox_end__']})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('my_tuples') == (-100, 100, 'Aquaveo', 'Test', 1, False)
        assert form.is_valid() is True

    def test_tuples_false(self):
        my_param = MyParamTuple()
        request_data = QueryDict('', mutable=True)
        request_data.update({'my_tuples': ['-100', '100', 'Aquaveo', 'Test', 'False', '1']})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('my_tuples') == (-100, 100, 'Aquaveo', 'Test', False, 1)
        assert form.is_valid() is True

    def test_numerictuples(self):
        my_param = MyParamNumericTuple()
        request_data = QueryDict('', mutable=True)
        request_data.update({'my_numeric_tuples': ['-100', '100', '1']})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('my_numeric_tuples') == (-100, 100, 1)
        assert form.is_valid() is True

    def test_magnitude(self):
        my_param = MyParamMagnitude()
        request_data = QueryDict('', mutable=True)
        request_data.update({'magnitude': '0.99'})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('magnitude') == 0.99
        assert form.is_valid() is True

    def test_number(self):
        my_param = MyParamNumber()
        request_data = QueryDict('', mutable=True)
        request_data.update({'number': '15'})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('number') == 15
        assert form.is_valid() is True

    def test_number_bound_initial(self):
        my_param = MyParamNumber()
        request_data = QueryDict('', mutable=True)
        request_data.update({'number': '15'})
        form = ParamForm(request_data, initial={'number': '14'}, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('number') == 15
        assert form.is_valid() is True

    def test_number_invalid(self):
        my_param = MyParamNumber()
        request_data = QueryDict('', mutable=True)
        request_data.update({'number': 'abc'})
        form = ParamForm(request_data, param=my_param)
        form.as_param()
        # Check result
        assert form.is_valid() is False

    def test_single_file_selector(self):
        my_param = MyParamFileSelector()
        request_data = QueryDict('', mutable=True)
        request_data.update({'single_file': 'test.sh'})
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('single_file') == 'test.sh'
        assert form.is_valid() is True

    def test_multiple_file_selector(self):
        my_param = MyParamMultiFileSelector()
        request_data = QueryDict('multiple_files=test.sh&multiple_files=setup.py', mutable=True)
        form = ParamForm(request_data, param=my_param)
        the_param = form.as_param()
        # Check result
        assert the_param.inspect_value('multiple_files') == ['test.sh', 'setup.py']
        assert form.is_valid() is True

    def test_multiple_file_selector_initial(self):
        my_param = MyParamMultiFileSelector()
        initial = QueryDict('multiple_files=test.sh', mutable=True)
        form = ParamForm(initial=initial, param=my_param)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('multiple_files') == ['test.sh']
        # is_valid should be false since the form is not bound.
        assert form.is_valid() is False

    def test_overwrite_widget(self):
        my_param = MyParamString()
        from django import forms
        from django.forms.widgets import Textarea

        widget_map = {
            param.parameterized.String:
                lambda po, p, name: forms.CharField(
                    initial=po.inspect_value(name) or p.default,
                    widget=Textarea,
                ),
        }
        request_data = QueryDict('', mutable=True)
        request_data.update({'param_string': 'test string'})
        form = ParamForm(request_data, param=my_param, widget_map=widget_map)
        the_param = form.as_param()

        # Check result
        assert the_param.inspect_value('param_string') == 'test string'
        assert form.is_valid() is True
        assert isinstance(form.fields['param_string'].widget, Textarea) is True
