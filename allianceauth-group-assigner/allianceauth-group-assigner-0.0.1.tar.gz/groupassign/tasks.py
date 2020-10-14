import logging

from celery import shared_task
from django.dispatch import receiver

from django.db.models.signals import pre_save
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from .models import StateGroupBinding

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

@shared_task
def check_all_bindings():
    bindings = StateGroupBinding.objects.all()

    for sgb in bindings:
        users = User.objects.filter(profile__state=sgb.state)
        for usr in users:
            if sgb.groups.all() not in usr.groups.all():
                usr.groups.add(*sgb.groups.all())

