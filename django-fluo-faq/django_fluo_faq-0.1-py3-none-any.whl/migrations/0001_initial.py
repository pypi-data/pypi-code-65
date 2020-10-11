# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django.conf import settings
from django.db import models, migrations
import django.utils.timezone
import fluo.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordering', fluo.db.models.fields.OrderField(default=0, help_text='Ordered', verbose_name='ordering', blank=True)),
                ('created_at', fluo.db.models.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('last_modified_at', fluo.db.models.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('uuid', models.CharField(help_text='for preview.', max_length=36, null=True, verbose_name='uuid field', blank=True)),
                ('status', fluo.db.models.fields.StatusField(default='draft', help_text='If should be displayed or not.', max_length=10, verbose_name='status', choices=[('draft', 'Draft'), ('published', 'Published')])),
                ('event_date', models.DateTimeField(help_text='Date which post refers to.', null=True, verbose_name='Post date', blank=True)),
                ('pub_date_begin', models.DateTimeField(help_text='When post publication date begins.', null=True, verbose_name='Publication date begin', blank=True)),
                ('pub_date_end', models.DateTimeField(help_text='When post publication date ends.', null=True, verbose_name='Publication date end', blank=True)),
                ('title', models.CharField(unique=True, max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug field')),
                ('abstract', models.CharField(help_text='A brief description of the post', max_length=255, null=True, verbose_name='Abstract', blank=True)),
                ('text', models.TextField(null=True, verbose_name='Default text', blank=True)),
                ('note', models.TextField(verbose_name='Note', blank=True)),
                ('owner', models.ForeignKey(related_name='faq_faq_owned', blank=True, to=settings.AUTH_USER_MODEL, help_text='Post owner.', on_delete=models.CASCADE, null=True, verbose_name='owned by')),
            ],
            options={
                'verbose_name': 'faq',
                'verbose_name_plural': 'faq',
            },
        ),
        migrations.CreateModel(
            name='FaqTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(db_index=True, max_length=5, verbose_name='language', choices=[('it', 'Italian'), ('en', 'English')])),
                ('title', models.CharField(unique=True, max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug field')),
                ('abstract', models.CharField(help_text='A brief description', max_length=255, verbose_name='Abstract')),
                ('text', models.TextField(verbose_name='Body')),
                ('parent', models.ForeignKey(related_name='translations', verbose_name='faq', on_delete=models.CASCADE, to='faq.Faq')),
            ],
            options={
                'verbose_name': 'faq translation',
                'verbose_name_plural': 'faq translations',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', fluo.db.models.fields.StatusField(default='active', help_text='Is active?', max_length=10, verbose_name='status', choices=[('active', 'Active'), ('inactive', 'Inactive')])),
                ('ordering', fluo.db.models.fields.OrderField(default=0, help_text='Ordered', verbose_name='ordering', blank=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', models.SlugField(editable=False, help_text='A "slug" is a unique URL-friendly title for the object automatically generated from the "name" field.', unique=True, verbose_name='slug')),
                ('default', models.BooleanField(default=False, help_text='Is the default one?', verbose_name='default')),
            ],
            options={
                'verbose_name': 'topic',
                'verbose_name_plural': 'topics',
            },
        ),
        migrations.AddField(
            model_name='faq',
            name='topics',
            field=models.ManyToManyField(to='faq.Topic', verbose_name='topics'),
        ),
        migrations.AddField(
            model_name='faq',
            name='users',
            field=models.ManyToManyField(help_text='Post visible to these users, if empty is visible to all users.', related_name='faq_faq_visible', verbose_name='Visible only to', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='faqtranslation',
            unique_together=set([('title', 'slug'), ('parent', 'language')]),
        ),
    ]
