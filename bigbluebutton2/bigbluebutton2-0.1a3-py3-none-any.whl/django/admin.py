"""Stub for registering models in django-admin for those who want it."""
from django.conf import settings
from django.contrib import admin

from .models import APIToken, BigBlueButton, BigBlueButtonGroup, Meeting

if "django.contrib.admin" in settings.INSTALLED_APPS:
    admin.site.register(APIToken)
    admin.site.register(BigBlueButton)
    admin.site.register(BigBlueButtonGroup)
    admin.site.register(Meeting)
