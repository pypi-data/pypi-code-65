from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django_tables2 import SingleTableView

from .mixins import NextMixin, TitleMixin


class ListView(TitleMixin, SingleTableView):
    template_name = "core/list.html"
    paginate_by = 30


class CreateView(TitleMixin, NextMixin, generic.CreateView):
    template_name = "core/edit.html"

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if self.get_form().is_valid():
                messages.success(
                    self.request,
                    format_lazy(
                        _("{entity} created successfully."),
                        entity=self.model._meta.verbose_name,
                    ),
                )
            return response
        except ValidationError as error:
            messages.error(self.request, error.message)
        return HttpResponseRedirect(self.get_success_url())


class UpdateView(TitleMixin, NextMixin, generic.UpdateView):
    template_name = "core/edit.html"

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if self.get_form().is_valid():
                messages.success(
                    self.request,
                    format_lazy(
                        _("{entity} updated successfully."),
                        entity=self.model._meta.verbose_name,
                    ),
                )
            return response
        except ValidationError as error:
            messages.error(self.request, error.message)
        return HttpResponseRedirect(self.get_success_url())


class DeleteView(TitleMixin, generic.DeleteView):
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(
                self.request,
                format_lazy(
                    _("{entity} deleted successfully."),
                    entity=self.model._meta.verbose_name,
                ),
            )
            return response
        except ValidationError as error:
            messages.error(self.request, error.message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.request.META["HTTP_REFERER"]
