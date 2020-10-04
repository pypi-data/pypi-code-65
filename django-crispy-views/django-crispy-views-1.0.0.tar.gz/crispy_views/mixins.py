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
