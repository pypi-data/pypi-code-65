from django.db.models.manager import BaseManager
from queryset import GuardianQuerySet
from django.db import models

class GuardianManager(BaseManager.from_queryset(GuardianQuerySet), models.Manager):
    pass


