import ipywidgets as widgets
from traitlets import List as _List, TraitType as _TraitType, Type as _Type, Any as _Any, Unicode as _Unicode, Bool as _Bool, Int as _Int, validate as _validate, TraitError as _TraitError
from .table_traitlet import DataTable as _DataTable

# See js/lib/example.js for the frontend counterpart to this file.

@widgets.register
class InteractiveTable(widgets.DOMWidget):
    """Widget for an interactive table utilizing jquery datatable."""

    # Name of the widget view class in front-end
    _view_name = _Unicode('InteractiveTableView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = _Unicode('InteractiveTableModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = _Unicode('ipydatatable').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = _Unicode('ipydatatable').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = _Unicode('^0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = _Unicode('^0.1.0').tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    table = _DataTable([]).tag(sync=True)
    column_filter = _Bool(True).tag(sync=True)
    text_limit = _Int(1000).tag(sync=True)
    sort_column = _Unicode("None").tag(sync=True)
    selected_data = _DataTable([]).tag(sync=True)
    columns = _DataTable([]).tag(sync=True)
    init_state = _Unicode("hide").tag(sync=True)

    # Basic validator for the floater value
    @_validate('init_state')
    def _valid_filter(self, proposal):
        if isinstance(proposal['value'], str):
            if proposal['value'] == "show" or proposal['value'] == "hide":
                return proposal['value']
            else:
                raise _TraitError('Invalid column filter value. Approriate values are show or hide')
        raise _TraitError('Invalid column filter value. Provide a string.')

    # Basic validator for the floater value
    @_validate('column_filter')
    def _valid_filter(self, proposal):
        if isinstance(proposal['value'], bool):
            return proposal['value']
        raise _TraitError('Invalid column filter value. Provide a boolean.')

    # Basic validator for the label value
    @_validate('text_limit')
    def _valid_text_limit(self, proposal):
        if isinstance(proposal['value'], int):
            return proposal['value']
        raise _TraitError('Invalid text limit value. Provide an int.')

    # Basic validator for the icon value
    @_validate('sort_column')
    def _valid_sort_column(self, proposal):
        if isinstance(proposal['value'], str):
            return proposal['value']
        raise _TraitError('Invalid sort column value. Provide a string.')

    def innotebook():
        import subprocess
        output = subprocess.getoutput('jupyter nbextension list')
        if 'ipydatatable/extension \x1b[32m enabled' not in output:
            print('Enable ipydatatable extension by running "jupyter nbextension enable --py --sys-prefix ipydatatable" in a terminal and refresh screen')
        else:
            print("ipydatatable: If no table displayed on initialization, please refresh window.")

    innotebook()
