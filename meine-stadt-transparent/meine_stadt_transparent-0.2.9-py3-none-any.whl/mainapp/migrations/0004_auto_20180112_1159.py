# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-12 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20171222_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendaitem',
            name='result',
            field=models.TextField(blank=True, null=True),
        ),
    ]
