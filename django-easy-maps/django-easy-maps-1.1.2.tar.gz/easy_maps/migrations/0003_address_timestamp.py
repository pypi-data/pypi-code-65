# Generated by Django 2.1.7 on 2019-03-29 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easy_maps', '0002_auto_20190329_0541'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
