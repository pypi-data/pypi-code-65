from django.shortcuts import redirect
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


class NextMixin:
    success_url = None

    def get(self, request, *args, **kwargs):
        next_url = request.GET.get('next', None)
        if next_url is None:
            http_referer = request.META.get('HTTP_REFERER', None)
            if http_referer is not None:
                http_referer = '/'.join(['', http_referer.split('/', 3).pop()])
            return redirect(request.path + '?next=' + (http_referer or ''))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next') or self.success_url or '/'


class TitleMixin:

    @property
    def list_title(self):
        return self.model._meta.verbose_name_plural

    @property
    def create_title(self):
        return format_lazy(
            _("Add new {entity}"),
            entity=self.model._meta.verbose_name,
        )

    @property
    def update_title(self):
        return format_lazy(
            _("Edit {entity}"),
            entity=self.model._meta.verbose_name,
        )

    @property
    def delete_title(self):
        return format_lazy(
            _("Delete {entity}"),
            entity=self.model._meta.verbose_name,
        )


class TemplateFactoryMixin:
    def create_hidden_input(self, name, value):
        return f"""<input type="hidden" name="{name}" value="{value}">"""

    def create_action_link(self, title, target, style="primary"):
        return f"""<a class="btn btn-{style} btn-sm mr-2" href="{target}">{title.capitalize()}</a>"""

    def create_form_button(self, title, style="primary"):
        return f"""<button class="btn btn-{style} btn-sm mr-2">{title.capitalize()}</button>"""

    def create_post_form(
        self, action, confirmation=None, confirmationTitle="confirm!", children=()
    ):
        confirmation = (
            f"onsubmit=\"swalConfirmSubmit(event, '{confirmation.capitalize()}', '{confirmationTitle.capitalize()}')\""
            if confirmation
            else ""
        )
        body = "".join(children) + self.create_hidden_input(
            "csrfmiddlewaretoken", self.context["csrf_token"]
        )
        return f"""<form class="d-inline mr-2" method="POST" action="{action}" {confirmation}>{body}</form>"""

    def create_action_form(
        self, label, label_class="primary", action="", confirmation=None, fields=None
    ):
        fields = fields or {}
        return self.create_post_form(
            action=action,
            confirmation=confirmation,
            confirmationTitle=label,
            children=(
                *[
                    self.create_hidden_input(name, value)
                    for name, value in fields.items()
                ],
                self.create_form_button(label, label_class),
            ),
        )
