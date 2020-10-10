from django.db import models
from django_eveonline_connector.models import EveCharacter, EveCorporation, EveAlliance
from django.contrib.auth.models import User, Group



class EveTimer(models.Model):
    name = models.CharField(max_length=64)
    type = models.ForeignKey("EveTimerType", on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=32, null=True, blank=True)
    timer = models.DateTimeField(auto_now=False, auto_now_add=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class EveTimerType(models.Model):
    bootstrap_colors = (
        ("primary", "Blue"),
        ("secondary", "Gray"),
        ("success", "Green"),
        ("danger", "Red"),
        ("warning", "Yellow"),
        ("info", "Light Blue"),
        ("light", "White"),
        ("dark", "Black")
    )
    
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=32, choices=bootstrap_colors)

    def __str__(self):
        return self.name