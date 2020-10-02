# Generated by Django 2.2.14 on 2020-09-24 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0079_add_tle_field_in_observation_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satellite',
            name='status',
            field=models.CharField(choices=[('alive', 'alive'), ('dead', 'dead'), ('future', 'future'), ('re-entered', 're-entered')], default='alive', max_length=10),
        ),
    ]
