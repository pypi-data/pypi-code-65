from django.db import models
from django.contrib.auth.models import Group
from allianceauth.authentication.models import State

class StateGroupBinding(models.Model):
    state = models.OneToOneField(State, on_delete=models.CASCADE, related_name='state_assign')
    groups = models.ManyToManyField(Group, related_name='group_assign', blank=True)

    def __str__(self):
        return self.state.name
