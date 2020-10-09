from django import forms

from django_eveonline_doctrine_manager.models import (EveDoctrineManagerTag, 
    EveDoctrineCategory, 
    EveDoctrineRole,
    EveDoctrine,
    EveFitting,
    EveSkillPlan)

class EveDoctrineForm(forms.Form):
    name = forms.CharField(max_length=32, required=True)
    description = forms.CharField(widget=forms.Textarea)
    tags = forms.ModelMultipleChoiceField(
        queryset=EveDoctrineManagerTag.objects.all(),
        required=False)
    category = forms.ModelChoiceField(
        queryset=EveDoctrineCategory.objects.all(),
        required=False)

class EveFittingForm(forms.Form):
    name = forms.CharField(max_length=32, required=True)
    description = forms.CharField(widget=forms.Textarea)
    fitting = forms.CharField(widget=forms.Textarea)
    refit_of = forms.ModelChoiceField(
        queryset=EveFitting.objects.all(),
        required=False
    )
    doctrines = forms.ModelMultipleChoiceField(
        queryset=EveDoctrine.objects.all(),
        required=True
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=EveDoctrineManagerTag.objects.all(),
        required=False)
    roles = forms.ModelMultipleChoiceField(
        queryset=EveDoctrineRole.objects.all(),
        required=False)


class EveSkillPlanForm(forms.Form):
    name = forms.CharField(max_length=32, required=True)
    description = forms.CharField(widget=forms.Textarea)
    skills = forms.CharField(widget=forms.Textarea)
    doctrines = forms.ModelMultipleChoiceField(
        queryset=EveDoctrine.objects.all(),
        required=True
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=EveDoctrineManagerTag.objects.all(),
        required=False)
    role = forms.ModelChoiceField(
        queryset=EveDoctrineRole.objects.all(),
        required=False)

