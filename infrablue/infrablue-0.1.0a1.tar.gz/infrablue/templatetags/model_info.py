from django import template
register = template.Library()


@register.simple_tag(name="verbose_name")
def get_verbose_field_name(instance, field_name):
    """
    Returns the verbose_name of a field.
    """
    return instance._meta.get_field(field_name).verbose_name.title()


@register.simple_tag(name="help_text")
def get_help_text_field_name(instance, field_name):
    """
    Returns the help_text of a field.
    """
    return instance._meta.get_field(field_name).help_text.title()


@register.simple_tag(name="attr")
def get_attribute_value(instance, field_name):
    """
    Returns an attribute of a model instance.
    """
    return getattr(instance, field_name, None)
