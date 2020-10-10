from django import forms
from .models import EveTimer, EveTimerType

class EveTimerForm(forms.Form):
    name = forms.CharField(max_length=64, required=True)
    days = forms.IntegerField(min_value=0, required=True)
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=60, required=True)
    seconds = forms.IntegerField(min_value=0, max_value=60, required=True)
    type = forms.ModelChoiceField(queryset=EveTimerType.objects.all())
    location = forms.CharField(max_length=32, required=True)