from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table, TemplateColumn

from .mixins import TemplateFactoryMixin


class BaseTable(TemplateFactoryMixin, Table):
    class Meta:
        attrs = {
            "id": "pageTable",
            "class": "table table-striped table-bordered text-nowrap w-100 dataTable no-footer",
        }
        orderable = False


class ActionColumnMixin:
    def get_actions(self, value, record):
        return [self.create_action_link("edit", "{{ record.get_absolute_url }}")]

    def render_action(self, value, record):
        template = Template("".join(self.get_actions(value, record)))
        return template.render(Context({"record": record}))


class BaseActionTable(ActionColumnMixin, BaseTable):
    action = TemplateColumn(""" """, verbose_name=_("Action"))

    class Meta(BaseTable.Meta):
        sequence = ("...", "action")


class TruncatedTextColumn(Column):
    """A Column to limit to characters and add an ellipsis"""

    def __init__(
        self, truncate_length=100, *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.truncate_length = truncate_length

    def render(self, value):
        return (
            value[0 : (self.truncate_length - 3)] + "..."
            if len(value) > self.truncate_length
            else value
        )
