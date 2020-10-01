# Generated by Django 2.1.4 on 2018-12-21 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_auto_20181116_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpaper',
            name='change_request_of',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mainapp.HistoricalPaper'),
        ),
        migrations.AddIndex(
            model_name='searchstreet',
            index=models.Index(fields=['osm_id'], name='mainapp_sea_osm_id_a0c31a_idx'),
        ),
    ]
