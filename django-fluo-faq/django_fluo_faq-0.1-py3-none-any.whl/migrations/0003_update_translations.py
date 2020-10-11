from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0002_alter_abstract_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faqtranslation',
            name='abstract',
            field=models.TextField(blank=True, help_text='A brief description', null=True, verbose_name='Abstract'),
        ),
        migrations.AlterField(
            model_name='faqtranslation',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, verbose_name='Slug field'),
        ),
        migrations.AlterField(
            model_name='faqtranslation',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Body'),
        ),
        migrations.AlterField(
            model_name='faqtranslation',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Title'),
        ),
    ]
