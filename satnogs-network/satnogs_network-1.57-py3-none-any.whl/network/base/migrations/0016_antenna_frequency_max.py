# Generated by Django 1.10.6 on 2017-03-17 00:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_auto_20170304_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='antenna',
            name='frequency_max',
            field=models.FloatField(default=999999999, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
    ]
