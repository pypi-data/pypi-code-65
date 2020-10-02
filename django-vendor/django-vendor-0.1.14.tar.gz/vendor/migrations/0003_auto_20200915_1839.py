# Generated by Django 3.1 on 2020-09-15 18:39

from django.db import migrations, models
import django.db.models.deletion
import vendor.models.utils


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('vendor', '0002_auto_20200912_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprofile',
            name='site',
            field=models.ForeignKey(default=vendor.models.utils.set_default_site_id, on_delete=django.db.models.deletion.CASCADE, related_name='customer_profile', to='sites.site'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='site',
            field=models.ForeignKey(default=vendor.models.utils.set_default_site_id, on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='sites.site'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='site',
            field=models.ForeignKey(default=vendor.models.utils.set_default_site_id, on_delete=django.db.models.deletion.CASCADE, related_name='product_offers', to='sites.site'),
        ),
    ]
