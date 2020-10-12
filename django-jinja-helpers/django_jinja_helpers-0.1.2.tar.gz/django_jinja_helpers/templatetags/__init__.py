from crispy_forms.utils import render_crispy_form
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction
from webpack_loader import utils


@library.global_function
def render_bundle(bundle_name, extension=None, config='DEFAULT', attrs=''):
    tags = utils.get_as_tags(bundle_name, extension=extension, config=config, attrs=attrs)
    return mark_safe('\n'.join(tags))


@contextfunction
@library.global_function
def crispy(context, form, helper=None):
    return render_crispy_form(form, helper=helper, context=context)
