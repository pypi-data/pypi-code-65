# Generated by Django 2.1.5 on 2019-01-08 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filequeue',
            name='file',
        ),
        migrations.DeleteModel(
            name='FileQueue',
        ),
    ]
