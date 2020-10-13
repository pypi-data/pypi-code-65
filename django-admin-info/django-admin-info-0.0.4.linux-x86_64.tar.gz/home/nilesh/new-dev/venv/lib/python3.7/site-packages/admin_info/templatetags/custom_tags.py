import re
from django import template
from django.apps import apps
from django.db.models import Q
from django.db import transaction
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from email.errors import HeaderParseError
from email.parser import HeaderParser

try:
    import docutils.core
    import docutils.nodes
    import docutils.parsers.rst.roles
except ImportError:
    docutils_is_available = False
else:
    docutils_is_available = True

register = template.Library()

def get_all_tables():
    output = []
    for model in apps.get_models():
        d = dict(module_name=model.__module__, object_name=model.__name__)
        output.append(d)
    return output
table_data = get_all_tables()


def execute_modules(dict_data):
    mod = __import__(dict_data['module_name'], fromlist=[dict_data['object_name']])
    _class = getattr(mod, dict_data['object_name'])
    return _class


def camelCase(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]


@register.filter(name='get_cls_desc')
def get_cls_desc(cls):
    required_dict = {}
    for data in table_data:
        if data['object_name'] == cls['object_name']:
            required_dict = data
            break
    if required_dict:
        _class = execute_modules(dict_data=required_dict)
    else:
        _class = None
    if _class:
        string = _class.__doc__
        fields = _class._meta.get_fields()
        field_list = []
        for field in fields:
            field_list.append(field.name)
        field_string = '<p>{0}({1})</p>\n'.format(_class._meta.object_name, ', '.join(field_list))
        title, body, metadata = parse_docstring(string)
        if title != field_string:
            string = title
        else:
            string = ''
    else:
        string = ''
    return string


@register.filter(name='get_cls_detail')
def get_cls_detail(cls):
    model = cls.model
    model_name = model._meta.model_name
    fields = model._meta.get_fields()
    field_list = []
    for field in fields:
        field_list.append(field.name)
    field_string = '<p>{0}({1})</p>\n'.format(model._meta.object_name, ', '.join(field_list))
    title, body, metadata = parse_docstring(model.__doc__)
    title = title and parse_rst(title, 'model', _('model:') + model_name)
    body = body and parse_rst(body, 'model', _('model:') + model_name)
    if title == field_string:
        title = None
        body = None
    string = render_to_string('admin/summary.tpl', {'title': title, 'body': body})

    return string


def trim_docstring(docstring):
    if not docstring or not docstring.strip():
        return ''
    lines = docstring.expandtabs().splitlines()
    indent = min(len(line) - len(line.lstrip()) for line in lines if line.lstrip())
    trimmed = [lines[0].lstrip()] + [line[indent:].rstrip() for line in lines[1:]]
    return "\n".join(trimmed).strip()


def parse_docstring(docstring):
    docstring = trim_docstring(docstring)
    parts = re.split(r'\n{2,}', docstring)
    title = parts[0]
    if len(parts) == 1:
        body = ''
        metadata = {}
    else:
        parser = HeaderParser()
        try:
            metadata = parser.parsestr(parts[-1])
        except HeaderParseError:
            metadata = {}
            body = "\n\n".join(parts[1:])
        else:
            metadata = dict(metadata.items())
            if metadata:
                body = "\n\n".join(parts[1:-1])
            else:
                body = "\n\n".join(parts[1:])
    return title, body, metadata

def parse_rst(text, default_reference_context, thing_being_parsed=None):
    overrides = {
        'doctitle_xform': True,
        'initial_header_level': 3,
        "default_reference_context": default_reference_context,
        'raw_enabled': False,
        'file_insertion_enabled': False,
    }
    thing_being_parsed = thing_being_parsed and '<%s>' % thing_being_parsed
    parts = docutils.core.publish_parts(
       text,
        source_path=thing_being_parsed, destination_path=None,
        writer_name='html', settings_overrides=overrides,
    )
    return mark_safe(parts['fragment'])
