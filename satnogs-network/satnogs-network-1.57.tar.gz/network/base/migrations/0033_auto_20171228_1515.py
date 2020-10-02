# Generated by Django 1.11.7 on 2017-12-28 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_auto_20171224_1703'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='station',
            options={'ordering': ['-status']},
        ),
        migrations.RemoveField(
            model_name='station',
            name='active',
        ),
        migrations.AddField(
            model_name='observation',
            name='testing',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='station',
            name='status',
            field=models.IntegerField(choices=[(2, 'Online'), (1, 'Testing'), (0, 'Offline')], default=0),
        ),
        migrations.AddField(
            model_name='station',
            name='testing',
            field=models.BooleanField(default=False),
        ),
    ]
