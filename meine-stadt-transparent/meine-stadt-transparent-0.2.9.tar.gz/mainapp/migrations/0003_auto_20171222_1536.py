# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-22 14:36
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import migrations
from django.db import migrations


def update_site(apps, schema_editor):
    Site.objects.get_or_create(name=settings.PRODUCT_NAME, domain=settings.REAL_HOST)


class Migration(migrations.Migration):
    dependencies = [
        ('mainapp', '0002_auto_20171222_1521'),
    ]

    operations = [
        migrations.RunPython(update_site),

    ]
