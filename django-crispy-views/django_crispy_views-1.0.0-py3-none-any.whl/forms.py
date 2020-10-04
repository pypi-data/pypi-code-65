from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Reset, Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet


class BaseFormMixin:
    layout = None
    fields_layout = None
    form_actions_layout = None
    submit_btn_text = _("Submit")
    helper_attrs = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customize()

    def customize(self, default_helper_attrs=None):
        self.helper = FormHelper(self)
        self.helper_attrs = {
            "include_media": False,
            **(default_helper_attrs or {}),
            **self.helper_attrs,
        }
        for key, value in self.helper_attrs.items():
            setattr(self.helper, key, value)

        if self.layout:
            self.helper.layout = self.layout
        else:
            self.helper.layout = Layout(
                self.fields_layout or self.helper.layout,
                FormActions(
                    self.form_actions_layout
                    or StrictButton(
                        self.submit_btn_text,
                        type="submit",
                        css_class="btn btn-primary float-right",
                    ),
                ),
            )

        extra_kwargs = {}
        if hasattr(self.__class__, "Meta"):
            extra_kwargs = getattr(self.__class__.Meta, "extra_kwargs", {})

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                if field.empty_label == "---------":
                    field.empty_label = "Choose One"
            if field.label is not None:
                field.label = field.label.capitalize()
            if field_name in extra_kwargs:
                for key, value in extra_kwargs[field_name].items():
                    setattr(field, key, value)


class HorizontalFormMixin:
    def customize(self, default_helper_attrs=None):
        super().customize(
            {
                "form_class": "form-horizontal",
                "label_class": "col-sm-3",
                "field_class": "col-sm-9",
                **(default_helper_attrs or {}),
            }
        )


class VerticalForm(BaseFormMixin, forms.Form):
    pass


class HorizontalForm(HorizontalFormMixin, BaseFormMixin, forms.Form):
    pass


class VerticalModelForm(BaseFormMixin, forms.ModelForm):
    pass


class HorizontalModelForm(HorizontalFormMixin, BaseFormMixin, forms.ModelForm):
    pass


class FilterForm(FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = getattr(self.__class__.Meta, "labels", {})
        for field_name, field in self.form.fields.items():
            if field_name in labels:
                label = labels[field_name]
                label = label.field.verbose_name if hasattr(label, "field") else label
                field.label = label.capitalize()
            if isinstance(field, forms.NullBooleanField):
                field.widget.choices[0] = ("unknown", "Any")

    def get_form_class(self):
        form_class = super().get_form_class()
        helper = FormHelper()
        helper.form_method = "GET"
        helper.add_input(Submit("submit", _("Search")))
        helper.add_input(
            Reset(
                "reset",
                _("Clear Filters"),
                css_class="btn btn-danger",
                onclick=f'location.href="{self.request.path}"',
            )
        )
        form_class.helper = helper
        return form_class
