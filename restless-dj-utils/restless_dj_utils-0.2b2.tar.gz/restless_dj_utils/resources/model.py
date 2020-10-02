"""
Resource mixin that provides helpers for creating API's from django models.
"""
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from restless.exceptions import UnprocessableEntity, NotFound


class ModelResourceMixin:
    """
    Provides a Resource.get_queryset and Resource.get_object like in
    Django class based views. Also provides a Resource.process_form helper to
    process forms and return standard/consistent errors.
    """

    model = None
    queryset = None

    def process_form(self, form_class, error_class=UnprocessableEntity, **kwargs):
        """
        Process a form based on the passed config
        """

        form = form_class(self.data, **kwargs)
        if not form.is_valid():
            try:
                msg = form.errors["__all__"][0]
            except (KeyError, IndexError):
                msg = "Validation failed, Check errors for details"

            errors = {k: v for k, v in form.errors.items() if k != "__all__"}
            raise error_class(
                {"errNo": error_class.status, "errMsg": msg, "errors": errors}
            )
        return form.save()

    def get_queryset(self):
        """
        Returns the objects for the list API and for consideration by the
        Resource.get_object() helper.
        """

        if self.queryset is None:
            if self.model:
                return self.model._default_manager.all()
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        return self.queryset.all()

    def get_object(self, pk):
        """
        Return the object used in the detail, update and delete APIs.
        """
        try:
            return self.get_queryset().get(pk=pk)
        except (ObjectDoesNotExist, ValueError):
            raise NotFound(
                {
                    "errNo": 404,
                    "errDev": "Object with that id does not exist",
                    "errMsg": "The object you specified does not exist",
                }
            )

    def order_queryset(self, qs, fields, default=None):
        """
        Helper method to order a queryset based on user provided options
        """

        ordering = self.request.GET.get("ordering", default)
        if ordering is not None:
            order_by = []
            for field in ordering.lower().split(","):
                try:
                    field, order = field.split(":")
                except ValueError:
                    continue
                if order in ("asc", "desc") and field in fields.keys():
                    order = "-" if order == "desc" else ""
                    order_by.append(f"{order}{fields[field]}")

            if len(order_by) > 0:
                qs = qs.order_by(*order_by)

        return qs
